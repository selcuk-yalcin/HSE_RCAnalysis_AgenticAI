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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to import agents and shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
from agents.actionplan_agent import ActionPlanAgent
from agents.pdf_report_agent import PDFReportAgent

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
    print(f"📊 OpenRouter API Key configured: {bool(os.getenv('OPENROUTER_API_KEY'))}")
    
    # Verify API key is set
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  WARNING: No API key found in environment variables!")
        print("⚠️  Set OPENROUTER_API_KEY in .env file")
        return
    
    try:
        # Initialize agents WITHOUT config parameter (they read from .env internally)
        overview_agent = OverviewAgent()
        print("✅ Overview Agent initialized")
        
        assessment_agent = AssessmentAgent()
        print("✅ Assessment Agent initialized")
        
        rootcause_agent = RootCauseAgent()
        print("✅ Root Cause Agent initialized (DeepSeek V3 + Claude 3.5 Sonnet)")
        
        actionplan_agent = ActionPlanAgent()
        print("✅ Action Plan Agent initialized")
        
        pdf_agent = PDFReportAgent()
        print("✅ PDF Report Agent initialized")
        
        print("🎉 All agents ready!")
        print(f"🔑 Using API Key: {api_key[:20]}...{api_key[-10:]}")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        import traceback
        traceback.print_exc()
        # Don't crash - let healthcheck show the error
        pass

# In-memory storage (replace with database in production)
incidents_db = {}

# Helper function to transform V2 format to frontend format
def transform_v2_to_frontend(part3_raw: dict) -> dict:
    """
    Transform rootcause_agent_v2 output to frontend-compatible format
    
    V2 Format:
    {
        "analysis_branches": [
            {
                "immediate_cause": {...},
                "why_chain": [...],
                "root_cause": {...}
            }
        ],
        "final_root_causes": [...]
    }
    
    Frontend Format:
    {
        "immediate_causes": [...],
        "underlying_causes": [...],
        "root_causes": [...]
    }
    """
    immediate_causes = []
    underlying_causes = []
    root_causes = []
    
    # Extract from analysis branches
    for branch in part3_raw.get("analysis_branches", []):
        # Immediate cause (A/B categories)
        imm = branch.get("immediate_cause", {})
        if imm:
            immediate_causes.append({
                "code": imm.get("code", ""),
                "category": imm.get("category_type", ""),
                "description": imm.get("cause_tr", imm.get("cause", "")),
                "evidence": imm.get("evidence_tr", "")
            })
        
        # Underlying causes (Why 1-4)
        why_chain = branch.get("why_chain", [])
        for why in why_chain:
            underlying_causes.append({
                "level": why.get("level", 0),
                "question": why.get("question_tr", ""),
                "answer": why.get("answer_tr", ""),
                "branch": branch.get("branch_number", 0)
            })
        
        # Root cause (C/D categories, Why 5)
        root = branch.get("root_cause", {})
        if root:
            root_causes.append({
                "code": root.get("code", ""),
                "category": root.get("category_type", ""),
                "description": root.get("cause_tr", root.get("cause", "")),
                "explanation": root.get("explanation_tr", ""),
                "branch": branch.get("branch_number", 0)
            })
    
    return {
        "immediate_causes": immediate_causes,
        "underlying_causes": underlying_causes,
        "root_causes": root_causes,
        "analysis_method": part3_raw.get("analysis_method", "HSG245 Hierarchical 5-Why"),
        "incident_summary": part3_raw.get("incident_summary", ""),
        "final_report_tr": part3_raw.get("final_report_tr", ""),
        # Keep original V2 data for debugging
        "_v2_raw": part3_raw
    }

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
    incident_id: str = ""  # Optional - can be inferred from URL path
    how_happened: str  # Main detailed investigation field (REQUIRED)
    location: str = ""  # Optional legacy fields
    who_involved: str = ""
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
    # Check if agents are initialized
    if overview_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Overview Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
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
    if assessment_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Assessment Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
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
    NOTE: Can work standalone with just incident description for testing
    """
    if rootcause_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Root Cause Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = incidents_db[incident_id]
    
    # Part 1 & Part 2 are now optional - will use defaults if not available
    part1_raw = incident.get("part1")
    part2_raw = incident.get("part2")
    
    # Ensure they are dicts, not None or strings
    if not part1_raw or not isinstance(part1_raw, dict):
        part1_data = {
            "incident_id": incident_id,
            "description": "To be reviewed - testing mode",
            "brief_details": {},
            "note": "Part 1 not completed - for testing purposes only"
        }
    else:
        part1_data = part1_raw
    
    if not part2_raw or not isinstance(part2_raw, dict):
        part2_data = {
            "event_type": "Accident",
            "investigation_level": "Medium level",
            "note": "Part 2 not completed - for testing purposes only"
        }
    else:
        part2_data = part2_raw
    
    try:
        # Process with Root Cause Agent (V2 format)
        part3_raw = rootcause_agent.analyze_root_causes(
            part1_data,
            part2_data,
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
        
        # Transform V2 format to frontend-compatible format
        part3_data = transform_v2_to_frontend(part3_raw)
        
        # Update database
        incidents_db[incident_id]["part3"] = part3_data
        incidents_db[incident_id]["status"] = "investigated"
        
        return {
            "success": True,
            "data": part3_data
        }
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"❌ Part 3 ERROR: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@app.post("/api/v1/incidents/{incident_id}/actionplan")
async def generate_action_plan(incident_id: str):
    """
    Part 4: Generate action plan with ActionPlan Agent
    """
    if actionplan_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Action Plan Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
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
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    return {
        "status": "healthy" if all_agents_ready else "degraded",
        "agents": agents_status,
        "api_key_configured": bool(api_key),
        "api_key_source": "OPENROUTER_API_KEY" if os.getenv("OPENROUTER_API_KEY") else "OPENAI_API_KEY" if os.getenv("OPENAI_API_KEY") else "none",
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
