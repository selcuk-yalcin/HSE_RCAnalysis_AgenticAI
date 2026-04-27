"""
FastAPI Backend for HSE Investigation System
Connects admin panel with AI agents
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import sys
import os
import traceback
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional, Tuple, Type
import json
from celery.result import AsyncResult

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to import agents and shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.actionplan_agent import ActionPlanAgent
from agents.claude_skill_pdf_agent import ClaudeSkillPDFAgent as PDFReportAgent
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from agents.hitl_question_service import next_hitl_questions, next_why_probe_questions
from agents.model_constants import (
    resolve_openrouter_chat_model,
    resolve_openrouter_dspy_model,
    resolve_openrouter_docx_model,
)
from shared.tenant_store import (
    get_tenant_store,
    total_incidents_across_tenants,
    all_tenants_summary,
    DEFAULT_TENANT_ID,
)
from shared.tenant_auth import resolve_tenant_id
from shared.hybrid_cache import hybrid_get, hybrid_set
from shared.oracle_memory import merge_oracle_into_investigation, upsert_context, list_recent
from shared.ops_celery import celery_inspect_snapshot
from shared.redis_client import get_redis_client
from agents.pattern_analyzer import aggregate_root_cause_codes, summarize_status

try:
    from celery_app import celery_app
    from tasks.pipeline_tasks import run_pipeline_task
except Exception:  # noqa: BLE001
    celery_app = None
    run_pipeline_task = None

# V3.1 (DSPy) öncelikli; dspy veya init hatasında V2'ye düşülür
_RootCauseV3_1: Optional[Type] = None
_v3_1_import_error: Optional[BaseException] = None
try:
    from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1 as _RootCauseV3_1
except BaseException as exc:  # noqa: BLE001 — ImportError ve bağımlılık zinciri
    _v3_1_import_error = exc

app = FastAPI(
    title="HSE Investigation API",
    description="Backend API for HSG245 Multi-Agent Investigation System",
    version="1.0.0"
)

TenantId = Annotated[str, Depends(resolve_tenant_id)]

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
# Hangi kök neden motorunun yüklendiği (health / log)
rootcause_engine_info = "not_initialized"


def _env_bool(name: str, default: bool = False) -> bool:
    """Parse YES/NO style env vars. Unset → default."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _use_celery_pipeline() -> bool:
    return _env_bool("USE_CELERY_PIPELINE", False)


def _hitl_cache_ttl_seconds() -> int:
    raw = (os.getenv("HITL_CACHE_TTL_SECONDS") or "900").strip()
    try:
        return max(60, int(raw))
    except Exception:  # noqa: BLE001
        return 900


def _init_root_cause_agent(use_rag: bool) -> Tuple[object, str]:
    """
    Önce RootCauseAgentV3_1 (DSPy); import veya __init__ başarısızsa RootCauseAgentV2.
    ROOTCAUSE_ENGINE=v2|legacy ile doğrudan V2 zorlanabilir.
    """
    force_v2 = os.getenv("ROOTCAUSE_ENGINE", "").strip().lower() in (
        "v2",
        "2",
        "legacy",
    )
    if force_v2:
        agent = RootCauseAgentV2(use_rag=use_rag)
        return agent, "v2 (ROOTCAUSE_ENGINE forced)"

    if _RootCauseV3_1 is None:
        err = repr(_v3_1_import_error) if _v3_1_import_error else "unknown"
        print(f"⚠️  V3.1 import edilemedi, V2 kullanılıyor: {err}")
        agent = RootCauseAgentV2(use_rag=use_rag)
        return agent, f"v2 (v3.1 import failed: {err})"

    try:
        agent = _RootCauseV3_1(use_rag=use_rag)
        return agent, "v3.1"
    except Exception as e:
        print(f"⚠️  V3.1 başlatılamadı, V2 kullanılıyor: {e}")
        traceback.print_exc()
        agent = RootCauseAgentV2(use_rag=use_rag)
        return agent, f"v2 (fallback after v3.1 init error: {e})"


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    global overview_agent, assessment_agent, rootcause_agent, actionplan_agent, pdf_agent
    global rootcause_engine_info
    
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
        
        # RAG (SentenceTransformer + Mongo) startup'ı çok uzatır; Railway healthcheck zaman aşımına düşer.
        # Üretimde varsayılan kapalı — ROOTCAUSE_USE_RAG=1 ile açın (MONGODB_URI gerekli).
        use_rag = _env_bool("ROOTCAUSE_USE_RAG", False)
        rootcause_agent, rootcause_engine_info = _init_root_cause_agent(use_rag)
        print(
            "✅ Root Cause Agent initialized "
            f"[{rootcause_engine_info}] "
            f"({'RAG on' if use_rag else 'static KB, RAG off — set ROOTCAUSE_USE_RAG=1 to enable'})"
        )
        
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

def _incidents(tenant_id: str) -> dict:
    return get_tenant_store(tenant_id).incidents_db


def _jobs(tenant_id: str) -> dict:
    return get_tenant_store(tenant_id).jobs_db


_INCIDENT_REDIS_TTL_SECONDS = max(
    3600,
    int((os.getenv("INCIDENT_REDIS_TTL_SECONDS") or "2592000").strip() or "2592000"),
)


def _incident_redis_key(tenant_id: str, incident_id: str) -> str:
    return f"hse:incident:{tenant_id}:{incident_id}"


def _save_incident_record(tenant_id: str, incident_id: str, incident: dict) -> None:
    """Store incident in local memory and Redis for cross-instance consistency."""
    _incidents(tenant_id)[incident_id] = incident
    client = get_redis_client()
    if client is None:
        return
    try:
        client.setex(
            _incident_redis_key(tenant_id, incident_id),
            _INCIDENT_REDIS_TTL_SECONDS,
            json.dumps(incident, ensure_ascii=False, default=str),
        )
    except Exception:  # noqa: BLE001
        # Redis write is best effort; in-memory remains source of truth for this process.
        pass


def _load_incident_record(tenant_id: str, incident_id: str) -> Optional[dict]:
    store = _incidents(tenant_id)
    incident = store.get(incident_id)
    if incident:
        return incident

    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(_incident_redis_key(tenant_id, incident_id))
        if not raw:
            return None
        incident = json.loads(raw)
        if isinstance(incident, dict):
            store[incident_id] = incident
            return incident
    except Exception:  # noqa: BLE001
        return None
    return None


def _require_incident_record(tenant_id: str, incident_id: str) -> dict:
    incident = _load_incident_record(tenant_id, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _job_stage_message(stage: str) -> str:
    mapping = {
        "queued": "Kuyruga alindi",
        "investigate": "Kok neden analizi calisiyor",
        "actionplan": "Aksiyon plani olusturuluyor",
        "completed": "Pipeline tamamlandi",
        "failed": "Pipeline hata ile sonlandi",
    }
    return mapping.get(stage, stage)


def _set_job_state(tenant_id: str, job_id: str, **kwargs):
    job = _jobs(tenant_id).get(job_id)
    if not job:
        return
    job.update(kwargs)
    job["updated_at"] = _utc_now_iso()


def _default_part1_data(incident_id: str) -> dict:
    return {
        "incident_id": incident_id,
        "description": "To be reviewed - testing mode",
        "brief_details": {},
        "note": "Part 1 not completed - for testing purposes only",
    }


def _default_part2_data() -> dict:
    return {
        "event_type": "Accident",
        "investigation_level": "Medium level",
        "note": "Part 2 not completed - for testing purposes only",
    }


def _sync_incident_from_pipeline_result(result_payload: dict):
    incident_id = (result_payload or {}).get("incident_id")
    if not incident_id:
        return
    tenant_id = (result_payload or {}).get("tenant_id") or "default"
    store = _incidents(tenant_id)
    incident = store.get(incident_id)
    if not incident:
        return

    part3 = result_payload.get("part3")
    part4 = result_payload.get("part4")
    if part3:
        incident["part3"] = part3
        incident["status"] = "investigated"
    if part4:
        incident["part4"] = part4
        incident["status"] = "completed"
    _save_incident_record(tenant_id, incident_id, incident)


def _normalize_celery_job(task_id: str) -> dict:
    if celery_app is None:
        return {
            "job_id": task_id,
            "status": "failed",
            "stage": "failed",
            "progress": 100,
            "message": "Celery app not configured",
            "error": "Celery app not configured",
        }

    async_result = AsyncResult(task_id, app=celery_app)
    state = async_result.state
    info = async_result.info
    meta = info if isinstance(info, dict) else {}

    if state == "SUCCESS":
        result_payload = async_result.result if isinstance(async_result.result, dict) else {}
        _sync_incident_from_pipeline_result(result_payload)
        return {
            "job_id": task_id,
            "tenant_id": result_payload.get("tenant_id") or meta.get("tenant_id"),
            "incident_id": result_payload.get("incident_id") or meta.get("incident_id"),
            "status": "completed",
            "stage": result_payload.get("stage", "completed"),
            "progress": int(result_payload.get("progress", 100)),
            "message": result_payload.get("message", "Pipeline tamamlandi"),
            "result": result_payload,
            "error": None,
        }

    if state in ("FAILURE", "REVOKED"):
        return {
            "job_id": task_id,
            "tenant_id": meta.get("tenant_id"),
            "incident_id": meta.get("incident_id"),
            "status": "failed",
            "stage": "failed",
            "progress": 100,
            "message": "Pipeline hata ile sonlandi",
            "result": None,
            "error": str(info),
        }

    if state in ("STARTED", "PROGRESS", "RETRY"):
        return {
            "job_id": task_id,
            "tenant_id": meta.get("tenant_id"),
            "incident_id": meta.get("incident_id"),
            "status": "running",
            "stage": meta.get("stage", "running"),
            "progress": int(meta.get("progress", 10)),
            "message": meta.get("message", "Pipeline calisiyor"),
            "result": None,
            "error": None,
        }

    # PENDING and unknown
    return {
        "job_id": task_id,
        "tenant_id": meta.get("tenant_id"),
        "incident_id": meta.get("incident_id"),
        "status": "queued",
        "stage": "queued",
        "progress": int(meta.get("progress", 0)),
        "message": meta.get("message", "Kuyruga alindi"),
        "result": None,
        "error": None,
    }

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
    why_probe_answers: list[dict] | None = None
    output_language: str = ""  # e.g. en, tr — passed to root cause agent
    oracle_context: str = ""  # optional; merged server-side from Oracle store when empty


class PipelineStartRequest(BaseModel):
    """Asenkron RCA + ActionPlan pipeline baslatma payload'i."""
    how_happened: str
    location: str = ""
    who_involved: str = ""
    activities: str = ""
    working_conditions: str = ""
    safety_procedures: str = ""
    injuries: str = ""
    why_probe_answers: list[dict] | None = None
    output_language: str = ""

class HitlQuestionsRequest(BaseModel):
    """Dinamik HITL soruları (knowledge_base / disambiguation tabanlı); LLM gerektirmez."""

    how_happened: str = ""
    root_cause_initial: str = ""
    answered_ids: list[str] = []
    immediate_causes: list[dict] | None = None
    immediate_code: str = ""
    why_level: int = 0
    current_why_question: str = ""
    previous_why_answer: str = ""
    mode: str = "global"
    batch_size: int = 1
    known_fields: list[str] = []

class PDFGenerateRequest(BaseModel):
    incident_id: str


def _validate_artifact_paths(artifacts: dict) -> bool:
    if not isinstance(artifacts, dict):
        return False
    required = ("docx_path", "html_path", "decision_tree_path")
    for key in required:
        val = (artifacts.get(key) or "").strip()
        if not val:
            return False
        if not Path(val).exists():
            return False
    return True


def _generate_report_artifacts(tenant_id: str, incident_id: str) -> dict:
    """Generate DOCX + HTML + decision tree artifacts and return absolute paths."""
    if pdf_agent is None:
        raise HTTPException(status_code=503, detail="Report agent is not initialized")

    incident = _require_incident_record(tenant_id, incident_id)
    if incident.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail="All parts must be completed before generating report",
        )

    try:
        cached_artifacts = incident.get("report_artifacts") or {}
        if _validate_artifact_paths(cached_artifacts):
            return {
                "docx_path": str(Path(cached_artifacts["docx_path"]).resolve()),
                "html_path": str(Path(cached_artifacts["html_path"]).resolve()),
                "decision_tree_path": str(Path(cached_artifacts["decision_tree_path"]).resolve()),
            }

        part3_data = incident.get("part3") or {}
        part3_v2 = part3_data.get("_v2_raw") if isinstance(part3_data, dict) else None
        report_payload = {
            "ref_no": incident_id,
            "part1": incident.get("part1", {}),
            "part2": incident.get("part2", {}),
            # SkillBasedDocxAgent expects part3_rca (raw V2 preferred).
            "part3_rca": part3_v2 if isinstance(part3_v2, dict) else part3_data,
            "part4": incident.get("part4", {}),
        }
        preferred_language = (
            (incident.get("output_language") or "").strip()
            or ((part3_v2 or {}).get("output_language") if isinstance(part3_v2, dict) else "")
            or (part3_data.get("output_language") if isinstance(part3_data, dict) else "")
        )

        active_report_agent = pdf_agent
        try:
            docx_generated = active_report_agent.generate_report(
                report_payload,
                preferred_language=preferred_language,
            )
        except Exception as primary_exc:
            # Railway runtime may not have local SKILL.md for ClaudeSkillPDFAgent.
            # Fallback to SkillBasedDocxAgent to guarantee DOCX+HTML generation.
            if "SKILL.md not loaded" not in str(primary_exc):
                raise
            print("⚠️  ClaudeSkillPDFAgent unavailable (SKILL.md missing). Falling back to SkillBasedDocxAgent.")
            active_report_agent = SkillBasedDocxAgent()
            docx_generated = active_report_agent.generate_report(
                report_payload,
                preferred_language=preferred_language,
            )

        docx_path = Path(docx_generated).resolve()
        html_path = docx_path.with_suffix(".html")
        decision_tree_path = docx_path.with_name(f"{docx_path.stem}_decision_tree.html")

        if not html_path.exists():
            raise HTTPException(status_code=500, detail="HTML report file could not be generated")
        if not decision_tree_path.exists():
            raise HTTPException(status_code=500, detail="Decision tree report file could not be generated")

        artifacts = {
            "docx_path": str(docx_path),
            "html_path": str(html_path.resolve()),
            "decision_tree_path": str(decision_tree_path.resolve()),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        incident["report_artifacts"] = artifacts
        _save_incident_record(tenant_id, incident_id, incident)

        return artifacts
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating report: {exc}") from exc


class OracleContextBody(BaseModel):
    summary: str
    incident_id: str = ""


class IncidentResponse(BaseModel):
    success: bool
    data: dict
    message: str = ""


async def _investigate_core(tenant_id: str, incident_id: str, investigation: InvestigationData) -> dict:
    if rootcause_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Root Cause Agent not initialized. Please check OPENROUTER_API_KEY environment variable.",
        )
    incident = _require_incident_record(tenant_id, incident_id)
    part1_raw = incident.get("part1")
    part2_raw = incident.get("part2")
    part1_data = part1_raw if part1_raw and isinstance(part1_raw, dict) else _default_part1_data(incident_id)
    part2_data = part2_raw if part2_raw and isinstance(part2_raw, dict) else _default_part2_data()
    inv_dump = investigation.model_dump()
    try:
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
                "injuries": investigation.injuries,
                "why_probe_answers": investigation.why_probe_answers or [],
                "oracle_context": (inv_dump.get("oracle_context") or ""),
                "output_language": (inv_dump.get("output_language") or ""),
            },
        )
        part3_data = transform_v2_to_frontend(part3_raw)
        incident["output_language"] = (inv_dump.get("output_language") or "").strip()
        incident["part3"] = part3_data
        incident["status"] = "investigated"
        _save_incident_record(tenant_id, incident_id, incident)
        return {"success": True, "data": part3_data}
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"❌ Part 3 ERROR: {error_details}")
        raise HTTPException(status_code=500, detail=error_details) from e


async def _actionplan_core(tenant_id: str, incident_id: str) -> dict:
    if actionplan_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Action Plan Agent not initialized. Please check OPENROUTER_API_KEY environment variable.",
        )
    incident = _require_incident_record(tenant_id, incident_id)
    if not incident.get("part3"):
        raise HTTPException(status_code=400, detail="Investigation not completed")
    part4_data = actionplan_agent.generate_action_plan(
        {
            "root_causes": incident["part3"]["root_causes"],
            "underlying_causes": incident["part3"]["underlying_causes"],
            "immediate_causes": incident["part3"]["immediate_causes"],
            "severity": incident["part2"]["investigation_level"],
        }
    )
    incident["part4"] = part4_data
    incident["status"] = "completed"
    _save_incident_record(tenant_id, incident_id, incident)
    return {"success": True, "data": part4_data}


async def _run_pipeline_job(job_id: str, incident_id: str, tenant_id: str, payload: dict):
    try:
        _set_job_state(
            tenant_id,
            job_id,
            status="running",
            stage="investigate",
            progress=15,
            message=_job_stage_message("investigate"),
        )

        merged_inv = merge_oracle_into_investigation(
            tenant_id, {**payload, "incident_id": incident_id}
        )
        investigation = InvestigationData(**merged_inv)

        part3_result = await _investigate_core(tenant_id, incident_id, investigation)

        _set_job_state(
            tenant_id,
            job_id,
            status="running",
            stage="actionplan",
            progress=70,
            message=_job_stage_message("actionplan"),
            part3_summary={
                "immediate": len((part3_result.get("data") or {}).get("immediate_causes") or []),
                "underlying": len((part3_result.get("data") or {}).get("underlying_causes") or []),
                "root": len((part3_result.get("data") or {}).get("root_causes") or []),
            },
        )

        part4_result = await _actionplan_core(tenant_id, incident_id)

        _set_job_state(
            tenant_id,
            job_id,
            status="completed",
            stage="completed",
            progress=100,
            message=_job_stage_message("completed"),
            result={
                "tenant_id": tenant_id,
                "incident_id": incident_id,
                "part3": part3_result.get("data"),
                "part4": part4_result.get("data"),
            },
            finished_at=_utc_now_iso(),
            error=None,
        )
    except HTTPException as he:
        _set_job_state(
            tenant_id,
            job_id,
            status="failed",
            stage="failed",
            progress=100,
            message=_job_stage_message("failed"),
            error=str(he.detail),
            finished_at=_utc_now_iso(),
        )
    except Exception as exc:  # noqa: BLE001
        _set_job_state(
            tenant_id,
            job_id,
            status="failed",
            stage="failed",
            progress=100,
            message=_job_stage_message("failed"),
            error=str(exc),
            finished_at=_utc_now_iso(),
        )

@app.get("/")
async def root():
    return {
        "service": "HSE Investigation API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": [
            "/api/v1/incidents",
            "/api/v1/incidents/{id}/hitl/questions",
            "/api/v1/incidents/{id}/pipeline/start",
            "/api/v1/jobs/{job_id}",
            "/ws/jobs/{job_id}",
            "/api/v1/health",
        ]
    }

@app.post("/api/v1/incidents/create", response_model=IncidentResponse)
async def create_incident(tenant_id: TenantId, incident: IncidentCreate):
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
        incident_record = {
            "id": incident_id,
            "tenant_id": tenant_id,
            "part1": part1_data,
            "part2": None,
            "part3": None,
            "part4": None,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        _save_incident_record(tenant_id, incident_id, incident_record)
        
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

@app.post("/api/v1/incidents/{incident_id}/hitl/questions")
async def hitl_dynamic_questions(tenant_id: TenantId, incident_id: str, body: HitlQuestionsRequest):
    """
    Sıralı HITL soruları: HSG245 disambiguation bankası + QuestionEngine (taxonomy / kb).
    """
    _require_incident_record(tenant_id, incident_id)
    bs = body.batch_size if body.batch_size and body.batch_size > 0 else 1
    bs = min(bs, 5)
    payload_for_key = {
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "body": body.model_dump(),
    }
    cached_payload, src = hybrid_get(tenant_id, "hitl_questions", payload_for_key)
    if cached_payload:
        return {"success": True, "data": cached_payload, "cached": True, "cache_layer": src}

    if (body.mode or "").lower() == "why_probe" or body.why_level > 0:
        payload = next_why_probe_questions(
            how_happened=body.how_happened or "",
            root_cause_initial=body.root_cause_initial or "",
            answered_ids=body.answered_ids or [],
            immediate_code=body.immediate_code or "",
            why_level=max(1, body.why_level or 1),
            current_why_question=body.current_why_question or "",
            previous_why_answer=body.previous_why_answer or "",
            batch_size=bs,
            known_fields=body.known_fields or [],
        )
    else:
        payload = next_hitl_questions(
            body.how_happened or "",
            body.root_cause_initial or "",
            body.answered_ids or [],
            body.immediate_causes,
            bs,
            known_fields=body.known_fields or [],
        )
    hybrid_set(
        tenant_id,
        "hitl_questions",
        payload_for_key,
        payload,
        _hitl_cache_ttl_seconds(),
    )
    return {"success": True, "data": payload, "cached": False, "cache_layer": "miss"}


@app.post("/api/v1/incidents/{incident_id}/assessment")
async def add_assessment(tenant_id: TenantId, incident_id: str, assessment: AssessmentData):
    """
    Part 2: Add assessment with Assessment Agent
    """
    if assessment_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Assessment Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
    try:
        incident = _require_incident_record(tenant_id, incident_id)
        
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
        incident["part2"] = part2_data
        incident["status"] = "assessed"
        _save_incident_record(tenant_id, incident_id, incident)
        
        return {
            "success": True,
            "data": part2_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/incidents/{incident_id}/investigate")
async def investigate_incident(tenant_id: TenantId, incident_id: str, investigation: InvestigationData):
    """
    Part 3: Full investigation with Root Cause Agent
    NOTE: Can work standalone with just incident description for testing
    """
    inv_dict = merge_oracle_into_investigation(tenant_id, investigation.model_dump())
    investigation = InvestigationData(**inv_dict)
    return await _investigate_core(tenant_id, incident_id, investigation)


@app.post("/api/v1/incidents/{incident_id}/pipeline/start")
async def start_pipeline_job(tenant_id: TenantId, incident_id: str, request: PipelineStartRequest):
    """
    Part 3 + Part 4 asenkron job baslatir.
    Frontend, /api/v1/jobs/{job_id} endpoint'ini poll ederek canli akis gosterir.
    """
    incident = _require_incident_record(tenant_id, incident_id)
    payload = merge_oracle_into_investigation(tenant_id, request.model_dump())

    if _use_celery_pipeline():
        if run_pipeline_task is None:
            raise HTTPException(status_code=503, detail="Celery task module not available.")

        part1_raw = incident.get("part1")
        part2_raw = incident.get("part2")
        part1_data = part1_raw if part1_raw and isinstance(part1_raw, dict) else _default_part1_data(incident_id)
        part2_data = part2_raw if part2_raw and isinstance(part2_raw, dict) else _default_part2_data()

        task = run_pipeline_task.delay(
            incident_id=incident_id,
            part1_data=part1_data,
            part2_data=part2_data,
            investigation_payload=payload,
            tenant_id=tenant_id,
        )

        return {
            "success": True,
            "data": {
                "job_id": task.id,
                "executor": "celery",
                "status": "queued",
                "stage": "queued",
                "progress": 0,
                "message": _job_stage_message("queued"),
            },
        }

    if rootcause_agent is None:
        raise HTTPException(status_code=503, detail="Service not ready. Root Cause Agent not initialized.")
    if actionplan_agent is None:
        raise HTTPException(status_code=503, detail="Service not ready. Action Plan Agent not initialized.")

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    _jobs(tenant_id)[job_id] = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "status": "queued",
        "stage": "queued",
        "progress": 0,
        "message": _job_stage_message("queued"),
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
        "finished_at": None,
        "result": None,
        "error": None,
    }
    asyncio.create_task(_run_pipeline_job(job_id, incident_id, tenant_id, payload))

    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "executor": "inprocess",
            "status": "queued",
            "stage": "queued",
            "progress": 0,
            "message": _job_stage_message("queued"),
        },
    }


@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str, tenant_id: str = Query(DEFAULT_TENANT_ID)):
    """In-process jobs require matching tenant query param or X-Tenant-ID header."""
    tid = tenant_id.strip() or DEFAULT_TENANT_ID
    if job_id in _jobs(tid):
        return {"success": True, "data": _jobs(tid)[job_id]}
    if _use_celery_pipeline():
        return {"success": True, "data": _normalize_celery_job(job_id)}
    raise HTTPException(status_code=404, detail="Job not found")


@app.websocket("/ws/jobs/{job_id}")
async def job_status_ws(
    websocket: WebSocket,
    job_id: str,
    tenant_id: str = Query(DEFAULT_TENANT_ID),
):
    """
    Job durumunu websocket ile stream eder.
    Frontend canli progres gosterimi icin kullanir.
    """
    await websocket.accept()
    tid = (tenant_id or DEFAULT_TENANT_ID).strip() or DEFAULT_TENANT_ID
    if job_id not in _jobs(tid) and not _use_celery_pipeline():
        await websocket.send_json(
            {"success": False, "error": "Job not found", "job_id": job_id}
        )
        await websocket.close(code=1008, reason="Job not found")
        return

    last_payload = None
    try:
        while True:
            job = _jobs(tid).get(job_id)
            if job is None and _use_celery_pipeline():
                job = _normalize_celery_job(job_id)
            if not job:
                await websocket.send_json(
                    {"success": False, "error": "Job not found", "job_id": job_id}
                )
                await websocket.close(code=1008, reason="Job not found")
                return

            payload = {"success": True, "data": job}
            payload_text = json.dumps(payload, sort_keys=True, default=str)
            if payload_text != last_payload:
                await websocket.send_json(payload)
                last_payload = payload_text

            if job.get("status") in ("completed", "failed"):
                await websocket.close(code=1000, reason="Job finished")
                return

            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return

@app.post("/api/v1/incidents/{incident_id}/actionplan")
async def generate_action_plan(tenant_id: TenantId, incident_id: str):
    """
    Part 4: Generate action plan with ActionPlan Agent
    """
    return await _actionplan_core(tenant_id, incident_id)

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident(tenant_id: TenantId, incident_id: str):
    """
    Get complete incident data
    """
    incident = _require_incident_record(tenant_id, incident_id)

    return {
        "success": True,
        "data": incident
    }

@app.get("/api/v1/incidents")
async def list_incidents(tenant_id: TenantId):
    """
    List all incidents
    """
    return {
        "success": True,
        "data": list(_incidents(tenant_id).values()),
        "count": len(_incidents(tenant_id)),
        "tenant_id": tenant_id,
    }


async def _probe_redis_ms() -> tuple[bool, Optional[float]]:
    import time
    from shared.redis_client import get_redis_client

    t0 = time.perf_counter()
    client = get_redis_client()
    if client is None:
        return False, None
    try:
        client.ping()
        return True, (time.perf_counter() - t0) * 1000
    except Exception:  # noqa: BLE001
        return False, None


async def _probe_mongo_ms() -> tuple[bool, Optional[float]]:
    import time

    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        return False, None
    t0 = time.perf_counter()

    def _ping():
        try:
            from pymongo import MongoClient
            from pymongo.server_api import ServerApi

            c = MongoClient(uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=3000)
            c.admin.command("ping")
            return True
        except Exception:  # noqa: BLE001
            return False

    ok = await asyncio.to_thread(_ping)
    ms = (time.perf_counter() - t0) * 1000
    return ok, ms if ok else None


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

    redis_ok, redis_ms = await _probe_redis_ms()
    mongo_ok, mongo_ms = await _probe_mongo_ms()
    
    return {
        "status": "healthy" if all_agents_ready else "degraded",
        "agents": agents_status,
        "rootcause_engine": rootcause_engine_info,
        "models": {
            "chat_default": resolve_openrouter_chat_model(),
            "dspy": resolve_openrouter_dspy_model(),
            "docx": resolve_openrouter_docx_model(),
        },
        "cache": {
            "hitl_cache_ttl_seconds": _hitl_cache_ttl_seconds(),
            "hybrid": {"redis_ping_ms": redis_ms, "redis_ok": redis_ok, "mongo_ping_ms": mongo_ms, "mongo_ok": mongo_ok},
        },
        "rag": {"enabled": _env_bool("ROOTCAUSE_USE_RAG", False)},
        "pipeline_executor": "celery" if _use_celery_pipeline() else "inprocess",
        "api_key_configured": bool(api_key),
        "api_key_source": "OPENROUTER_API_KEY" if os.getenv("OPENROUTER_API_KEY") else "OPENAI_API_KEY" if os.getenv("OPENAI_API_KEY") else "none",
        "incidents_count": total_incidents_across_tenants(),
        "tenants_summary": all_tenants_summary(),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/oracle/context")
async def post_oracle_context(tenant_id: TenantId, body: OracleContextBody):
    ok = upsert_context(tenant_id, body.summary, incident_id=body.incident_id)
    return {"success": ok, "tenant_id": tenant_id}


@app.get("/api/v1/oracle/context")
async def get_oracle_context(tenant_id: TenantId):
    return {"success": True, "data": list_recent(tenant_id)}


@app.get("/api/v1/ops/celery")
async def ops_celery(x_ops_key: Optional[str] = Header(None, alias="X-Ops-Key")):
    expected = (os.getenv("OPS_API_KEY") or "").strip()
    if expected and x_ops_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"success": True, "data": celery_inspect_snapshot(celery_app)}


@app.get("/api/v1/analytics/patterns")
async def analytics_patterns(tenant_id: TenantId):
    incidents = list(_incidents(tenant_id).values())
    return {
        "success": True,
        "tenant_id": tenant_id,
        "status_breakdown": summarize_status(incidents),
        "root_cause_codes": aggregate_root_cause_codes(incidents),
    }


@app.post("/api/v1/experimental/voice-bridge")
async def voice_bridge_stub():
    """Placeholder for future STT/TTS integration."""
    return {
        "success": False,
        "message": "Not implemented — connect Whisper/browser STT and forward text to existing investigation APIs.",
    }


@app.get("/api/v1/experimental/parallel-probes")
async def experimental_parallel_probes():
    """Runs Redis + Mongo probes concurrently via asyncio.gather."""
    import time

    t0 = time.perf_counter()
    r2, m2 = await asyncio.gather(_probe_redis_ms(), _probe_mongo_ms())
    wall_ms = (time.perf_counter() - t0) * 1000
    return {
        "success": True,
        "gather_wall_ms": round(wall_ms, 3),
        "redis": {"ok": r2[0], "ms": r2[1]},
        "mongo": {"ok": m2[0], "ms": m2[1]},
    }


@app.get("/api/v1/experimental/meta-learning")
async def meta_learning_info():
    return {
        "success": True,
        "status": "planned",
        "requirements": "Collect 30–50 cold-start incidents; run DSPy offline optimization; promote prompts to production.",
    }


@app.post("/api/v1/reports/generate")
async def generate_pdf_report(tenant_id: TenantId, request: PDFGenerateRequest):
    """
    Generate PDF report for completed incident
    """
    incident_id = request.incident_id
    artifacts = _generate_report_artifacts(tenant_id, incident_id)
    filepath = artifacts["docx_path"]
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"HSG245_Report_{incident_id}.docx",
        headers={
            "Content-Disposition": f"attachment; filename=HSG245_Report_{incident_id}.docx"
        },
    )


@app.post("/api/v1/reports/html")
async def generate_html_report(tenant_id: TenantId, request: PDFGenerateRequest):
    """
    Generate HTML report artifacts and return URLs for preview/download.
    """
    incident_id = request.incident_id
    artifacts = _generate_report_artifacts(tenant_id, incident_id)
    return {
        "success": True,
        "data": {
            "incident_id": incident_id,
            "html_url": f"/api/v1/reports/{incident_id}/html?download=0",
            "html_download_url": f"/api/v1/reports/{incident_id}/html?download=1",
            "decision_tree_url": f"/api/v1/reports/{incident_id}/decision-tree?download=0",
            "decision_tree_download_url": f"/api/v1/reports/{incident_id}/decision-tree?download=1",
            "html_path": artifacts["html_path"],
            "decision_tree_path": artifacts["decision_tree_path"],
        },
    }


@app.get("/api/v1/reports/{incident_id}/html")
async def get_html_report(
    tenant_id: TenantId,
    incident_id: str,
    download: int = Query(0),
):
    artifacts = _generate_report_artifacts(tenant_id, incident_id)
    html_path = artifacts["html_path"]
    if not Path(html_path).exists():
        raise HTTPException(status_code=404, detail="HTML report file not found")
    filename = f"HSG245_Report_{incident_id}.html"
    disposition = "attachment" if int(download) == 1 else "inline"
    with open(html_path, "rb") as f:
        html_bytes = f.read()
    return Response(
        content=html_bytes,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f"{disposition}; filename={filename}"},
    )


@app.get("/api/v1/reports/{incident_id}/decision-tree")
async def get_decision_tree_report(
    tenant_id: TenantId,
    incident_id: str,
    download: int = Query(0),
):
    artifacts = _generate_report_artifacts(tenant_id, incident_id)
    decision_tree_path = artifacts["decision_tree_path"]
    if not Path(decision_tree_path).exists():
        raise HTTPException(status_code=404, detail="Decision tree file not found")
    filename = f"HSG245_Report_{incident_id}_decision_tree.html"
    disposition = "attachment" if int(download) == 1 else "inline"
    with open(decision_tree_path, "rb") as f:
        decision_tree_bytes = f.read()
    return Response(
        content=decision_tree_bytes,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f"{disposition}; filename={filename}"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000
    )
