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

# Initialize agents
overview_agent = OverviewAgent(OPENAI_CONFIG)
pdf_agent = PDFReportAgent()

class IncidentCreate(BaseModel):
    reported_by: str
    description: str
    injury_description: str = ""
    forwarded_to: str = ""
    date_time: str = None
    
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

@app.post("/api/v1/incidents", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate):
    """
    Create new incident and process with Overview Agent
    Used by admin panel
    """
    try:
        incident_data = {
            "reported_by": incident.reported_by,
            "description": incident.description,
            "injury_description": incident.injury_description,
            "forwarded_to": incident.forwarded_to,
            "date_time": incident.date_time or datetime.now().strftime("%d.%m.%y %I:%M%p")
        }
        
        # Process with Overview Agent
        result = overview_agent.process_initial_report(incident_data)
        
        return IncidentResponse(
            success=True,
            data=result,
            message="Incident processed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing incident: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "agents": {
            "overview": "active",
            "pdf_generator": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/reports/generate")
async def generate_pdf_report(investigation_data: dict):
    """
    Generate PDF report from investigation data
    """
    try:
        # Generate PDF using PDF Report Agent
        filepath = pdf_agent.generate_report(investigation_data)
        
        # Return file response
        return FileResponse(
            filepath,
            media_type='application/pdf',
            filename=Path(filepath).name,
            headers={
                "Content-Disposition": f"attachment; filename={Path(filepath).name}"
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
