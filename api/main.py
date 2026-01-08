"""
FastAPI Backend for HSE Investigation System
Connects admin panel with AI agents
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to import agents and shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent import RootCauseAgent
from agents.actionplan_agent import ActionPlanAgent
from agents.pdf_report_agent import PDFReportAgent
from shared.config import OPENAI_CONFIG

app = FastAPI(
    title="HSE Investigation API",
    description="Backend API for HSG245 Multi-Agent Investigation System",
    version="1.0.0"
)

# CORS for Vercel admin panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://inferaworld-admin.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents with error handling
overview_agent = None
assessment_agent = None
rootcause_agent = None
actionplan_agent = None
pdf_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    global overview_agent, assessment_agent, rootcause_agent, actionplan_agent, pdf_agent
    
    print("🚀 Starting HSE Investigation API...")
    print(f"📊 OpenAI API Key configured: {bool(os.getenv('OPENAI_API_KEY'))}")
    
    try:
        overview_agent = OverviewAgent(OPENAI_CONFIG)
        print("✅ Overview Agent initialized")
        
        assessment_agent = AssessmentAgent(OPENAI_CONFIG)
        print("✅ Assessment Agent initialized")
        
        rootcause_agent = RootCauseAgent(OPENAI_CONFIG)
        print("✅ Root Cause Agent initialized")
        
        actionplan_agent = ActionPlanAgent(OPENAI_CONFIG)
        print("✅ Action Plan Agent initialized")
        
        pdf_agent = PDFReportAgent()
        print("✅ PDF Report Agent initialized")
        
        print("🎉 All agents ready!")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        # Don't crash - let healthcheck show the error
        pass

# In-memory storage (replace with database in production)
incidents_db = {}

# Request/Response Models
class IncidentCreate(BaseModel):
    reported_by: str
    description: str
    injury_description: str = ""
    forwarded_to: str = ""
    date_time: str = None
    event_category: str = ""

class AssessmentData(BaseModel):
    incident_id: str
    event_type: str
    actual_harm: str
    riddor_reportable: str

class InvestigationData(BaseModel):
    incident_id: str
    location: str
    who_involved: str
    how_happened: str
    activities: str = ""
    working_conditions: str = ""
    safety_procedures: str = ""
    injuries: str = ""

class PDFGenerateRequest(BaseModel):
    incident_id: str
    
class IncidentResponse(BaseModel):
    success: bool
    data: dict
    message: str = ""

@app.get("/")
async def root():
    return {
        "service": "HSE Investigation API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": [
            "/api/v1/incidents",
            "/api/v1/health"
        ]
    }

@app.post("/api/v1/incidents/create", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate):
    """
    Part 1: Create new incident and process with Overview Agent
    Returns incident ID and Part 1 data
    """
    try:
        incident_data = {
            "reported_by": incident.reported_by,
            "description": incident.description,
            "injury_description": incident.injury_description,
            "forwarded_to": incident.forwarded_to,
            "date_time": incident.date_time or datetime.now().strftime("%d.%m.%y %I:%M%p"),
            "event_category": incident.event_category
        }
        
        # Process with Overview Agent
        part1_data = overview_agent.process_initial_report(incident_data)
        
        # Store in database
        incident_id = part1_data["ref_no"]
        incidents_db[incident_id] = {
            "id": incident_id,
            "part1": part1_data,
            "part2": None,
            "part3": None,
            "part4": None,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        
        return IncidentResponse(
            success=True,
            data={"incident_id": incident_id, "part1": part1_data},
            message="Incident created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating incident: {str(e)}"
        )

@app.post("/api/v1/incidents/{incident_id}/assessment")
async def add_assessment(incident_id: str, assessment: AssessmentData):
    """
    Part 2: Add assessment with Assessment Agent
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    try:
        incident = incidents_db[incident_id]
        
        # Process with Assessment Agent
        part2_data = assessment_agent.assess_incident(
            incident["part1"],
            {
                "event_type": assessment.event_type,
                "actual_harm": assessment.actual_harm,
                "riddor_reportable": assessment.riddor_reportable
            }
        )
        
        # Update database
        incidents_db[incident_id]["part2"] = part2_data
        incidents_db[incident_id]["status"] = "assessed"
        
        return {
            "success": True,
            "data": part2_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/incidents/{incident_id}/investigate")
async def investigate_incident(incident_id: str, investigation: InvestigationData):
    """
    Part 3: Full investigation with Root Cause Agent
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = incidents_db[incident_id]
    
    if not incident["part2"]:
        raise HTTPException(status_code=400, detail="Assessment must be completed first")
    
    try:
        # Process with Root Cause Agent
        part3_data = rootcause_agent.analyze_root_causes(
            incident["part1"],
            incident["part2"],
            {
                "location": investigation.location,
                "who_involved": investigation.who_involved,
                "how_happened": investigation.how_happened,
                "activities": investigation.activities,
                "working_conditions": investigation.working_conditions,
                "safety_procedures": investigation.safety_procedures,
                "injuries": investigation.injuries
            }
        )
        
        # Update database
        incidents_db[incident_id]["part3"] = part3_data
        incidents_db[incident_id]["status"] = "investigated"
        
        return {
            "success": True,
            "data": part3_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/incidents/{incident_id}/actionplan")
async def generate_action_plan(incident_id: str):
    """
    Part 4: Generate action plan with ActionPlan Agent
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = incidents_db[incident_id]
    
    if not incident["part3"]:
        raise HTTPException(status_code=400, detail="Investigation not completed")
    
    try:
        # Process with ActionPlan Agent
        part4_data = actionplan_agent.generate_action_plan({
            "root_causes": incident["part3"]["root_causes"],
            "underlying_causes": incident["part3"]["underlying_causes"],
            "immediate_causes": incident["part3"]["immediate_causes"],
            "severity": incident["part2"]["investigation_level"]
        })
        
        # Update database
        incidents_db[incident_id]["part4"] = part4_data
        incidents_db[incident_id]["status"] = "completed"
        
        return {
            "success": True,
            "data": part4_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """
    Get complete incident data
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "success": True,
        "data": incidents_db[incident_id]
    }

@app.get("/api/v1/incidents")
async def list_incidents():
    """
    List all incidents
    """
    return {
        "success": True,
        "data": list(incidents_db.values()),
        "count": len(incidents_db)
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint - Railway uses this"""
    agents_status = {
        "overview": "active" if overview_agent else "not_initialized",
        "assessment": "active" if assessment_agent else "not_initialized",
        "rootcause": "active" if rootcause_agent else "not_initialized",
        "actionplan": "active" if actionplan_agent else "not_initialized",
        "pdf_generator": "active" if pdf_agent else "not_initialized"
    }
    
    all_agents_ready = all(status == "active" for status in agents_status.values())
    
    return {
        "status": "healthy" if all_agents_ready else "degraded",
        "agents": agents_status,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "incidents_count": len(incidents_db),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/reports/generate")
async def generate_pdf_report(request: PDFGenerateRequest):
    """
    Generate PDF report for completed incident
    """
    incident_id = request.incident_id
    
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = incidents_db[incident_id]
    
    if incident["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail="All parts must be completed before generating report"
        )
    
    try:
        # Prepare complete investigation data for PDF
        investigation_data = {
            "ref_no": incident_id,
            "part1": incident["part1"],
            "part2": incident["part2"],
            "part3": incident["part3"],
            "part4": {
                "actions": [
                    {
                        "measure": m["measure"],
                        "responsible": m["responsible"],
                        "target_date": m["target_date"]
                    }
                    for m in incident["part4"]["control_measures"]
                ]
            }
        }
        
        # Generate PDF using PDF Report Agent
        filepath = pdf_agent.generate_report(investigation_data)
        
        # Return file response
        return FileResponse(
            filepath,
            media_type='application/pdf',
            filename=f"HSG245_Report_{incident_id}.pdf",
            headers={
                "Content-Disposition": f"attachment; filename=HSG245_Report_{incident_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF report: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000
    )
