"""
FastAPI Backend for HSE Investigation System
Connects admin panel with AI agents
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
import sys
import os
import traceback
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional, Tuple, Type
import inspect
import json
import time
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
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from agents.hitl_question_service import (
    next_hitl_questions,
    next_immediate_causes_identify,
    next_root_cause_probe_questions,
    next_why_probe_questions,
    warm_hitl_resources,
)
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
from shared.owner_auth import resolve_owner_user_id
from shared.report_layout_config import resolve_report_layout, list_layout_catalog, normalize_layout_patch
from shared.plan_config import load_pricing_catalog
from shared.signed_links import verify_token
from shared import saved_reports_store
from shared import report_deliveries
from shared import token_account
from shared.usage_context import bind_usage_context, clear_usage_context
from shared.litellm_billing import install_litellm_billing_callback
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
OwnerUserId = Annotated[str, Depends(resolve_owner_user_id)]

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


def _raise_insufficient_tokens(message: str) -> None:
    raise HTTPException(
        status_code=402,
        detail={"code": "insufficient_tokens", "message": message},
    )


def _enforce_token_cost(tenant_id: str, owner_user_id: str, reason: str) -> None:
    if not token_account.enforcement_enabled():
        return
    cost = token_account.estimate_cost(reason)
    ok, msg = token_account.check_sufficient(tenant_id, owner_user_id, cost)
    if not ok:
        _raise_insufficient_tokens(msg)


def _hitl_cache_ttl_seconds() -> int:
    raw = (os.getenv("HITL_CACHE_TTL_SECONDS") or "900").strip()
    try:
        return max(60, int(raw))
    except Exception:  # noqa: BLE001
        return 900


def _hitl_question_budget_seconds() -> float:
    """HITL soru üretimi için sunucu tarafı süre bütçesi.

    Gateway timeout'undan (≈60s) düşük tutulur; aşılırsa 504 yerine retriable
    cevap döner ve arka plan görevi cache'i ısıtır.
    """
    raw = (os.getenv("HITL_QUESTION_BUDGET_SECONDS") or "40").strip()
    try:
        return max(5.0, float(raw))
    except Exception:  # noqa: BLE001
        return 40.0


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
        from agents.rca_cost_profile import get_rca_cost_profile, root_cause_agent_kwargs

        kwargs = root_cause_agent_kwargs(use_rag)
        agent = _RootCauseV3_1(**kwargs)
        prof = get_rca_cost_profile()
        return agent, f"v3.1 ({prof.name})"
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
        
        # RAG aktif varsayilan: ROOTCAUSE_USE_RAG=0 ile kapatılabilir.
        use_rag = _env_bool("ROOTCAUSE_USE_RAG", True)
        rootcause_agent, rootcause_engine_info = _init_root_cause_agent(use_rag)
        print(
            "✅ Root Cause Agent initialized "
            f"[{rootcause_engine_info}] "
            f"({'RAG on' if use_rag else 'static KB, RAG off — set ROOTCAUSE_USE_RAG=1 to enable'})"
        )
        
        actionplan_agent = ActionPlanAgent()
        print("✅ Action Plan Agent initialized")
        
        # Primary report generator: SkillBasedDocxAgent (DOCX + HTML + decision tree).
        # ClaudeSkillPDFAgent may exist in codebase but is not primary in API flow.
        pdf_agent = SkillBasedDocxAgent()
        print("✅ Report Agent initialized (SkillBasedDocxAgent)")
        
        print("🎉 All agents ready!")
        print(f"🔑 Using API Key: {api_key[:20]}...{api_key[-10:]}")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        import traceback
        traceback.print_exc()
        # Don't crash - let healthcheck show the error
        pass

    try:
        info = await asyncio.to_thread(saved_reports_store.ensure_collection)
        print(
            f"✅ Reports library ready: {info.get('database')}.{info.get('collection')} "
            f"(documents={info.get('document_count')})"
        )
    except Exception as rexc:
        print(f"⚠️  Reports library skipped — set MONGODB_URI on Railway: {rexc}")

    try:
        info = await asyncio.to_thread(token_account.ensure_collections)
        print(
            f"✅ Token accounts ready ({info.get('backend')}): "
            f"{info.get('account_documents')} accounts, {info.get('ledger_documents')} ledger rows"
        )
    except Exception as texc:
        print(f"⚠️  Token accounts init: {texc}")

    if install_litellm_billing_callback():
        print("✅ LiteLLM billing callback registered (API)")

    # HITL cold-start ısıtma:
    # model yükleme gecikmesini (gateway 504 kaynağı) ödememesi için arka planda.
    async def _warm_hitl() -> None:
        try:
            status = await asyncio.to_thread(warm_hitl_resources)
            print(
                f"✅ HITL kaynakları ısıtıldı: retriever={status.get('retriever')} "
                f"embedding={status.get('embedding')}"
            )
        except Exception as wexc:  # noqa: BLE001
            print(f"⚠️  HITL ısıtma atlandı: {wexc}")

    asyncio.create_task(_warm_hitl())


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


def _build_part1_fast(incident: "IncidentCreate") -> dict:
    """Map form fields to Part 1 without LLM (interactive HITL fast path)."""
    ref_no = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    description = (incident.description or "").strip()
    injury = (incident.injury_description or "").strip()
    what = description
    if injury and injury not in what:
        what = f"{what}\n{injury}".strip() if what else injury
    event_cat = (incident.event_category or "").strip()
    incident_type = event_cat or "Accident"
    return {
        "ref_no": ref_no,
        "reported_by": incident.reported_by or "",
        "date_time": incident.date_time or datetime.now().strftime("%d.%m.%y %I:%M%p"),
        "incident_type": incident_type,
        "brief_details": {
            "what": what[:2000],
            "where": incident.forwarded_to or "",
            "when": incident.date_time or "",
            "who": incident.reported_by or "",
            "emergency_measures": "",
        },
        "forwarded_to": incident.forwarded_to or "",
        "forwarded_date_time": "",
        "part1_source": "form_snapshot",
    }


def _build_part2_from_form_assessment(assessment: "AssessmentData") -> dict:
    """Map form assessment fields to Part 2 without LLM (interactive HITL fast path)."""
    harm = (assessment.actual_harm or "").strip()
    riddor_raw = (assessment.riddor_reportable or "").strip().lower()
    riddor_y = riddor_raw in ("yes", "y", "evet")
    if riddor_raw in ("no", "n", "hayır", "hayir"):
        riddor = "N"
    elif riddor_y:
        riddor = "Y"
    else:
        riddor = "N"

    harm_low = harm.lower()
    if "fatal" in harm_low or "major" in harm_low:
        level, priority = "High level", "High"
        team = ["H&S Manager", "Line Manager", "Technical Expert"]
    elif "serious" in harm_low:
        level, priority = "Medium level", "Medium"
        team = ["H&S Officer", "Line Manager"]
    elif "minor" in harm_low:
        level, priority = "Low level", "Low"
        team = ["H&S Officer", "Line Manager"]
    else:
        level, priority = "Basic", "Low"
        team = ["H&S Officer"]

    if riddor_y and level == "Basic":
        level, priority = "Medium level", "Medium"

    return {
        "type_of_event": assessment.event_type or "Accident",
        "actual_potential_harm": harm or "Minor",
        "riddor_reportable": riddor,
        "riddor_date_reported": datetime.now().strftime("%d.%m.%y") if riddor == "Y" else "",
        "accident_book_entry": "Y",
        "accident_book_date": datetime.now().strftime("%d.%m.%y"),
        "accident_book_ref": f"AB-{datetime.now().strftime('%Y%m%d')}",
        "investigation_level": level,
        "initial_assessment_by": "Form snapshot (HITL fast path)",
        "assessment_date": datetime.now().strftime("%d.%m.%y"),
        "further_investigation_required": "Y",
        "priority": priority,
        "investigation_team": team,
        "assessment_source": "form_snapshot",
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
    job_id = str(result_payload.get("last_pipeline_job_id") or "").strip()
    if job_id:
        incident["last_pipeline_job_id"] = job_id
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
            "activity_lines": meta.get("activity_lines") or [],
            "latest_activity": meta.get("latest_activity"),
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
            "activity_lines": meta.get("activity_lines") or [],
            "latest_activity": meta.get("latest_activity"),
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


class InteractiveBootstrapRequest(BaseModel):
    """Tek çağrıda Part 1 + Part 2 (LLM yok) — etkileşimli HITL form gönderimi."""
    reported_by: str
    description: str
    injury_description: str = ""
    forwarded_to: str = ""
    date_time: str = None
    event_category: str = ""
    event_type: str = ""
    actual_harm: str = ""
    riddor_reportable: str = ""


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
    root_cause_probe_answers: list[dict] | None = None  # P1.22: C/D kök neden aday probe cevapları
    output_language: str = ""  # e.g. en, tr — passed to root cause agent
    oracle_context: str = ""  # optional; merged server-side from Oracle store when empty
    analysis_model_preset: str = ""  # optional: quality | economy (DeepWhy form tier)


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
    root_cause_probe_answers: list[dict] | None = None  # P1.22
    output_language: str = ""
    analysis_model_preset: str = ""

class HitlQuestionsRequest(BaseModel):
    """Dinamik HITL soruları (LLM + taxonomy öncelikli, rule-based fallback)."""

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
    output_language: str = ""

class PDFGenerateRequest(BaseModel):
    incident_id: str
    report_layout: Optional[dict] = None
    force_regenerate: bool = False


class ReportLayoutRequest(BaseModel):
    report_layout: dict = {}
    force_regenerate: bool = True


class LibraryUpsertRequest(BaseModel):
    kind: str = "draft"  # draft | report
    snapshot: dict = {}
    title_hint: str = ""
    incident_id: str = ""
    report_ready: bool = False
    analysis_model_preset: str = ""
    item_id: str = ""


class LibraryFinalizeRequest(BaseModel):
    incident_id: str
    snapshot: dict = {}
    title_hint: str = ""
    analysis_model_preset: str = ""
    report_layout: Optional[dict] = None


class TokenTopUpRequest(BaseModel):
    amount: int
    owner_user_id: str = ""


class LibrarySaveHtmlRequest(BaseModel):
    incident_id: str
    snapshot: dict = {}
    title_hint: str = ""
    analysis_model_preset: str = ""
    report_html: str = ""
    decision_tree_html: str = ""


def _recover_incident_part3_from_pipeline(
    tenant_id: str,
    incident_id: str,
    incident: dict,
) -> dict:
    """Part3 Redis'e yazılmadan rapor istenirse Celery sonucundan veya Redis'ten kurtar."""
    if isinstance(incident.get("part3"), dict) and incident.get("part3"):
        return incident

    job_id = str(incident.get("last_pipeline_job_id") or "").strip()
    if job_id and celery_app is not None:
        try:
            async_result = AsyncResult(job_id, app=celery_app)
            if async_result.successful():
                payload = async_result.result if isinstance(async_result.result, dict) else {}
                part3 = payload.get("part3")
                part4 = payload.get("part4")
                if isinstance(part3, dict) and part3:
                    incident = dict(incident)
                    incident["part3"] = part3
                    if isinstance(part4, dict) and part4:
                        incident["part4"] = part4
                        incident["status"] = "completed"
                    else:
                        incident["status"] = "investigated"
                    _save_incident_record(tenant_id, incident_id, incident)
                    return incident
        except Exception:  # noqa: BLE001
            pass

    try:
        from shared.incident_persistence import load_incident_from_redis

        remote = load_incident_from_redis(tenant_id, incident_id)
        if isinstance(remote, dict) and isinstance(remote.get("part3"), dict) and remote.get("part3"):
            merged = {**incident, **remote}
            _incidents(tenant_id)[incident_id] = merged
            return merged
    except Exception:  # noqa: BLE001
        pass
    return incident


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


def _apply_report_layout_to_incident(
    tenant_id: str,
    incident_id: str,
    layout_patch: Optional[dict],
    *,
    force_regenerate: bool = True,
) -> dict:
    incident = _require_incident_record(tenant_id, incident_id)
    patch = normalize_layout_patch(layout_patch)
    layout = resolve_report_layout(incident, tenant_id=tenant_id, override=patch)
    incident["report_layout"] = layout
    incident["report_layout_snapshot"] = layout
    if force_regenerate:
        incident.pop("report_artifacts", None)
    _save_incident_record(tenant_id, incident_id, incident)
    return layout


def _generate_report_artifacts(
    tenant_id: str,
    incident_id: str,
    *,
    layout_override: Optional[dict] = None,
    force_regenerate: bool = False,
) -> dict:
    """Generate DOCX + HTML + decision tree artifacts and return absolute paths."""
    if pdf_agent is None:
        raise HTTPException(status_code=503, detail="Report agent is not initialized")

    incident = _require_incident_record(tenant_id, incident_id)

    if layout_override or force_regenerate:
        _apply_report_layout_to_incident(
            tenant_id,
            incident_id,
            layout_override,
            force_regenerate=bool(force_regenerate or layout_override),
        )
        incident = _require_incident_record(tenant_id, incident_id)

    # Önce daha önce üretilmiş artifact varsa doğrudan onu döndür.
    # Böylece incident part3 senkronizasyonu gecikse bile kullanıcı raporu açabilir.
    cached_artifacts = incident.get("report_artifacts") or {}
    if _validate_artifact_paths(cached_artifacts):
        return {
            "docx_path": str(Path(cached_artifacts["docx_path"]).resolve()),
            "html_path": str(Path(cached_artifacts["html_path"]).resolve()),
            "decision_tree_path": str(Path(cached_artifacts["decision_tree_path"]).resolve()),
        }

    # Bazı akışlarda job "completed" görünse de incident kaydına part3 yazımı gecikebiliyor.
    # Retry + Celery/Redis kurtarma penceresi.
    has_part3 = False
    for _ in range(20):
        incident = _recover_incident_part3_from_pipeline(tenant_id, incident_id, incident)
        has_part3 = isinstance(incident.get("part3"), dict) and bool(incident.get("part3"))
        cached_artifacts = incident.get("report_artifacts") or {}
        if has_part3 or _validate_artifact_paths(cached_artifacts):
            break
        time.sleep(1.0)
        incident = _require_incident_record(tenant_id, incident_id)
    has_part4 = isinstance(incident.get("part4"), dict) and bool(incident.get("part4"))
    if not has_part3:
        raise HTTPException(
            status_code=400,
            detail=(
                "Kök neden analizi (Part 3) henüz kayda yazılmadı. "
                "Analiz tamamlandıysa birkaç saniye bekleyip tekrar deneyin veya "
                "«Rapor ve karar ağacını buluta kaydet» ile HTML'i önce senkronize edin."
            ),
        )
    if not has_part4:
        if actionplan_agent is None:
            raise HTTPException(
                status_code=503,
                detail="Action Plan Agent not initialized; cannot auto-complete Part 4 for report generation",
            )
        try:
            part3_data = incident.get("part3") or {}
            incident["part4"] = actionplan_agent.generate_action_plan(
                {
                    "root_causes": part3_data.get("root_causes", []),
                    "underlying_causes": part3_data.get("underlying_causes", []),
                    "immediate_causes": part3_data.get("immediate_causes", []),
                    "severity": ((incident.get("part2") or {}).get("investigation_level", "")),
                }
            )
            incident["status"] = "completed"
            _save_incident_record(tenant_id, incident_id, incident)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Part 4 auto-completion failed before report generation: {exc}",
            ) from exc

    try:
        part3_data = incident.get("part3") or {}
        part3_v2 = part3_data.get("_v2_raw") if isinstance(part3_data, dict) else None
        layout = resolve_report_layout(incident, tenant_id=tenant_id)
        report_payload = {
            "ref_no": incident_id,
            "part1": incident.get("part1", {}),
            "part2": incident.get("part2", {}),
            # SkillBasedDocxAgent expects part3_rca (raw V2 preferred).
            "part3_rca": part3_v2 if isinstance(part3_v2, dict) else part3_data,
            "part4": incident.get("part4", {}),
            "report_layout": layout,
        }
        incident["report_layout_snapshot"] = layout
        preferred_language = (
            (incident.get("output_language") or "").strip()
            or ((part3_v2 or {}).get("output_language") if isinstance(part3_v2, dict) else "")
            or (part3_data.get("output_language") if isinstance(part3_data, dict) else "")
        )

        def _call_generate_report(agent_obj, payload, preferred_lang: str):
            sig = inspect.signature(agent_obj.generate_report)
            if "preferred_language" in sig.parameters:
                return agent_obj.generate_report(payload, preferred_language=preferred_lang)
            return agent_obj.generate_report(payload)

        active_report_agent = pdf_agent
        try:
            docx_generated = _call_generate_report(active_report_agent, report_payload, preferred_language)
        except Exception as primary_exc:
            # Ensure API always tries SkillBasedDocxAgent as safe fallback.
            if isinstance(active_report_agent, SkillBasedDocxAgent):
                raise
            print("⚠️  Primary report agent failed. Falling back to SkillBasedDocxAgent.")
            active_report_agent = SkillBasedDocxAgent()
            docx_generated = _call_generate_report(active_report_agent, report_payload, preferred_language)

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
                "root_cause_probe_answers": investigation.root_cause_probe_answers or [],
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


async def _run_pipeline_job(
    job_id: str,
    incident_id: str,
    tenant_id: str,
    payload: dict,
    owner_user_id: str = "anonymous",
):
    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="deepwhy",
        incident_id=incident_id,
        job_id=job_id,
    )
    try:
        await _run_pipeline_job_body(job_id, incident_id, tenant_id, payload, owner_user_id)
    finally:
        clear_usage_context()


async def _run_pipeline_job_body(
    job_id: str,
    incident_id: str,
    tenant_id: str,
    payload: dict,
    owner_user_id: str = "anonymous",
):
    try:
        _set_job_state(
            tenant_id,
            job_id,
            status="running",
            stage="investigate",
            progress=10,
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
            stage="investigate",
            progress=55,
            message="RCA tamamlandi, aksiyon plani hazirlaniyor",
        )

        _set_job_state(
            tenant_id,
            job_id,
            status="running",
            stage="actionplan",
            progress=62,
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

@app.post("/api/v1/incidents/create/fast", response_model=IncidentResponse)
async def create_incident_fast(tenant_id: TenantId, incident: IncidentCreate):
    """
    Part 1 from manual form only (no LLM). Used by interactive HITL so the UI
    is not blocked by Overview Agent OpenRouter calls before the chat tab opens.
    """
    try:
        part1_data = _build_part1_fast(incident)
        incident_id = part1_data["ref_no"]
        incident_record = {
            "id": incident_id,
            "tenant_id": tenant_id,
            "part1": part1_data,
            "part2": None,
            "part3": None,
            "part4": None,
            "created_at": datetime.now().isoformat(),
            "status": "created",
        }
        await asyncio.to_thread(
            _save_incident_record, tenant_id, incident_id, incident_record
        )
        return IncidentResponse(
            success=True,
            data={"incident_id": incident_id, "part1": part1_data},
            message="Incident created (fast path)",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating incident (fast): {str(e)}",
        ) from e


@app.post("/api/v1/incidents/bootstrap/interactive", response_model=IncidentResponse)
async def bootstrap_interactive_session(
    tenant_id: TenantId, body: InteractiveBootstrapRequest
):
    """
    Part 1 + Part 2 in one request (no LLM). Cuts gateway round-trips and avoids
    504 when Railway cold-starts between create and assessment calls.
    """
    try:
        incident = IncidentCreate(
            reported_by=body.reported_by,
            description=body.description,
            injury_description=body.injury_description,
            forwarded_to=body.forwarded_to,
            date_time=body.date_time,
            event_category=body.event_category,
        )
        part1_data = _build_part1_fast(incident)
        incident_id = part1_data["ref_no"]
        assessment = AssessmentData(
            incident_id=incident_id,
            event_type=body.event_type or body.event_category or "Accident",
            actual_harm=body.actual_harm or "",
            riddor_reportable=body.riddor_reportable or "",
        )
        part2_data = _build_part2_from_form_assessment(assessment)
        incident_record = {
            "id": incident_id,
            "tenant_id": tenant_id,
            "part1": part1_data,
            "part2": part2_data,
            "part3": None,
            "part4": None,
            "created_at": datetime.now().isoformat(),
            "status": "assessed",
        }
        await asyncio.to_thread(
            _save_incident_record, tenant_id, incident_id, incident_record
        )
        return IncidentResponse(
            success=True,
            data={
                "incident_id": incident_id,
                "part1": part1_data,
                "part2": part2_data,
            },
            message="Interactive session bootstrapped (fast path)",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error bootstrapping interactive session: {str(e)}",
        ) from e


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
async def hitl_dynamic_questions(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    incident_id: str,
    body: HitlQuestionsRequest,
):
    """
    Sıralı HITL soruları: HSG245 disambiguation + taxonomy + LLM.
    Her soru `response_mode`: `yes_no_unknown` | `free_text` | `choice` (chip listesi: `choice_options`, `choice_multi`).
    """
    _require_incident_record(tenant_id, incident_id)
    bs = body.batch_size if body.batch_size and body.batch_size > 0 else 1
    bs = min(bs, 5)
    output_language = (body.output_language or "").strip()
    payload_for_key = {
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "body": body.model_dump(),
        "output_language": output_language,
    }
    cached_payload, src = hybrid_get(tenant_id, "hitl_questions", payload_for_key)
    if cached_payload:
        return {"success": True, "data": cached_payload, "cached": True, "cache_layer": src}

    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="hitl",
        incident_id=incident_id,
    )
    mode = (body.mode or "").lower()

    def _compute_payload() -> dict:
        if mode == "immediate_identify":
            return next_immediate_causes_identify(
                how_happened=body.how_happened or "",
                root_cause_initial=body.root_cause_initial or "",
                output_language=output_language,
            )
        if mode == "rootcause_probe":
            return next_root_cause_probe_questions(
                how_happened=body.how_happened or "",
                root_cause_initial=body.root_cause_initial or "",
                answered_ids=body.answered_ids or [],
                immediate_code=body.immediate_code or "",
                batch_size=bs,
                known_fields=body.known_fields or [],
                output_language=output_language,
                tenant_id=tenant_id,
                incident_id=incident_id,
            )
        if mode == "why_probe" or body.why_level > 0:
            imm_tr = ""
            if body.immediate_causes:
                for c in body.immediate_causes:
                    if isinstance(c, dict) and str(c.get("code") or "").upper() == (
                        body.immediate_code or ""
                    ).strip().upper():
                        imm_tr = str(c.get("cause_tr") or "")
                        break
            return next_why_probe_questions(
                how_happened=body.how_happened or "",
                root_cause_initial=body.root_cause_initial or "",
                answered_ids=body.answered_ids or [],
                immediate_code=body.immediate_code or "",
                why_level=max(1, body.why_level or 1),
                current_why_question=body.current_why_question or "",
                previous_why_answer=body.previous_why_answer or "",
                batch_size=bs,
                known_fields=body.known_fields or [],
                output_language=output_language,
                immediate_cause_tr=imm_tr,
                tenant_id=tenant_id,
                incident_id=incident_id,
            )
        return next_hitl_questions(
            body.how_happened or "",
            body.root_cause_initial or "",
            body.answered_ids or [],
            body.immediate_causes,
            bs,
            known_fields=body.known_fields or [],
            output_language=output_language,
        )

    async def _compute_and_cache() -> dict:
        # Blocking üretimi event loop dışında çalıştır (head-of-line blocking önlenir).
        payload = await asyncio.to_thread(_compute_payload)
        hybrid_set(
            tenant_id,
            "hitl_questions",
            payload_for_key,
            payload,
            _hitl_cache_ttl_seconds(),
        )
        return payload

    task = asyncio.ensure_future(_compute_and_cache())
    # Timeout sonrası görev arka planda sürerse istisnası "never retrieved"
    # uyarısı vermesin diye sessizce tüket (cache zaten en iyi çaba).
    task.add_done_callback(lambda t: t.cancelled() or t.exception())
    try:
        # shield: timeout'ta görev iptal edilmez; arka planda tamamlanıp cache'i
        # ısıtır, böylece kullanıcının tekrar denemesi anında 200 döner.
        payload = await asyncio.wait_for(
            asyncio.shield(task), timeout=_hitl_question_budget_seconds()
        )
        return {"success": True, "data": payload, "cached": False, "cache_layer": "miss"}
    except asyncio.TimeoutError:
        # Üretim hâlâ sürüyor — 504 yerine retriable sinyal dön. İstemci kısa
        # bir bekleme sonrası tekrar dener ve sıcak cache'e düşer.
        return JSONResponse(
            status_code=202,
            content={
                "success": False,
                "retriable": True,
                "data": None,
                "cache_layer": "pending",
                "detail": "HITL soruları hazırlanıyor, lütfen birkaç saniye sonra tekrar deneyin.",
            },
        )
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"HITL question generation failed: {type(exc).__name__}: {exc}",
        ) from exc
    finally:
        clear_usage_context()


@app.post("/api/v1/incidents/{incident_id}/assessment")
async def add_assessment(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    incident_id: str,
    assessment: AssessmentData,
):
    """
    Part 2: Add assessment with Assessment Agent
    """
    if assessment_agent is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Assessment Agent not initialized. Please check OPENROUTER_API_KEY environment variable."
        )
    
    try:
        _enforce_token_cost(tenant_id, owner_user_id, "assessment")
        incident = _require_incident_record(tenant_id, incident_id)

        bind_usage_context(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            module="assessment",
            incident_id=incident_id,
        )
        try:
            part2_data = assessment_agent.assess_incident(
                incident["part1"],
                {
                    "event_type": assessment.event_type,
                    "actual_harm": assessment.actual_harm,
                    "riddor_reportable": assessment.riddor_reportable
                }
            )
        finally:
            clear_usage_context()
        
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


@app.post("/api/v1/incidents/{incident_id}/assessment/form")
async def add_assessment_from_form(tenant_id: TenantId, incident_id: str, assessment: AssessmentData):
    """
    Part 2 from manual form fields only (no LLM). Used by interactive HITL so the UI
    is not blocked by 4+ OpenRouter calls before the chat tab opens.
    """
    try:
        incident = _require_incident_record(tenant_id, incident_id)
        part2_data = _build_part2_from_form_assessment(assessment)
        incident["part2"] = part2_data
        incident["status"] = "assessed"
        await asyncio.to_thread(_save_incident_record, tenant_id, incident_id, incident)
        return {"success": True, "data": part2_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/incidents/{incident_id}/investigate")
async def investigate_incident(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    incident_id: str,
    investigation: InvestigationData,
):
    """
    Part 3: Full investigation with Root Cause Agent
    NOTE: Can work standalone with just incident description for testing
    """
    _enforce_token_cost(tenant_id, owner_user_id, "investigate")
    inv_dict = merge_oracle_into_investigation(tenant_id, investigation.model_dump())
    investigation = InvestigationData(**inv_dict)
    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="deepwhy",
        incident_id=incident_id,
    )
    try:
        result = await _investigate_core(tenant_id, incident_id, investigation)
    finally:
        clear_usage_context()
    return result


@app.post("/api/v1/incidents/{incident_id}/pipeline/start")
async def start_pipeline_job(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    incident_id: str,
    request: PipelineStartRequest,
):
    """
    Part 3 + Part 4 asenkron job baslatir.
    Frontend, /api/v1/jobs/{job_id} endpoint'ini poll ederek canli akis gosterir.
    """
    incident = _require_incident_record(tenant_id, incident_id)
    payload = merge_oracle_into_investigation(tenant_id, request.model_dump())
    _enforce_token_cost(tenant_id, owner_user_id, "pipeline")

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
            owner_user_id=owner_user_id,
        )
        incident["last_pipeline_job_id"] = task.id
        _save_incident_record(tenant_id, incident_id, incident)

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
    incident["last_pipeline_job_id"] = job_id
    _save_incident_record(tenant_id, incident_id, incident)
    asyncio.create_task(_run_pipeline_job(job_id, incident_id, tenant_id, payload, owner_user_id))

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
async def generate_action_plan(tenant_id: TenantId, owner_user_id: OwnerUserId, incident_id: str):
    """
    Part 4: Generate action plan with ActionPlan Agent
    """
    _enforce_token_cost(tenant_id, owner_user_id, "actionplan")
    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="deepwhy",
        incident_id=incident_id,
    )
    try:
        result = await _actionplan_core(tenant_id, incident_id)
    finally:
        clear_usage_context()
    return result

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
    reports_ping_ok, reports_ping_err = await asyncio.to_thread(saved_reports_store.ping_store)
    reports_location = saved_reports_store.store_location()
    reports_doc_count = await asyncio.to_thread(saved_reports_store.count_all_documents)

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
        "reports_library": {
            **reports_location,
            "ping_ok": reports_ping_ok,
            "ping_error": reports_ping_err or None,
            "document_count": reports_doc_count,
        },
        "token_accounts": {
            **token_account.store_location(),
            "enforcement_enabled": token_account.enforcement_enabled(),
            "ping_ok": (await asyncio.to_thread(token_account.ping_store))[0],
            "ping_error": (await asyncio.to_thread(token_account.ping_store))[1] or None,
        },
        "rag": {
            "enabled": _env_bool("ROOTCAUSE_USE_RAG", True),
            "abs_guidance": _env_bool("ROOTCAUSE_USE_ABS_RAG", False),
            "vector_barsel": _env_bool("ROOTCAUSE_USE_VECTOR_RAG", True),
        },
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


@app.get("/api/v1/reports/layout-options")
async def report_layout_options(lang: str = Query("tr", max_length=8)):
    """P0.9 — Cover templates, watermark modes, and section list for UI picker."""
    return {"success": True, "data": list_layout_catalog(lang)}


@app.put("/api/v1/incidents/{incident_id}/report-layout")
async def update_incident_report_layout(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    incident_id: str,
    body: ReportLayoutRequest,
):
    _ = owner_user_id
    layout = _apply_report_layout_to_incident(
        tenant_id,
        incident_id,
        body.report_layout,
        force_regenerate=body.force_regenerate,
    )
    return {"success": True, "data": {"incident_id": incident_id, "report_layout": layout}}


@app.post("/api/v1/reports/generate")
async def generate_pdf_report(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    request: PDFGenerateRequest,
):
    """
    Generate PDF report for completed incident
    """
    incident_id = request.incident_id
    _enforce_token_cost(tenant_id, owner_user_id, "report_docx")
    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="report",
        incident_id=incident_id,
    )
    try:
        artifacts = _generate_report_artifacts(
            tenant_id,
            incident_id,
            layout_override=request.report_layout,
            force_regenerate=request.force_regenerate,
        )
    finally:
        clear_usage_context()
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
async def generate_html_report(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    request: PDFGenerateRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """
    Generate HTML report artifacts and return URLs for preview/download.
    """
    incident_id = request.incident_id
    _enforce_token_cost(tenant_id, owner_user_id, "report_html")
    bind_usage_context(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        module="report",
        incident_id=incident_id,
    )
    try:
        artifacts = _generate_report_artifacts(
            tenant_id,
            incident_id,
            layout_override=request.report_layout,
            force_regenerate=request.force_regenerate,
        )
    finally:
        clear_usage_context()
    await _enqueue_report_delivery_email(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        recipient_email=(x_user_email or "").strip(),
        report_id=incident_id,
        incident_id=incident_id,
        artifacts=artifacts,
    )
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

def _read_artifact_files(artifacts: dict) -> tuple[str, str]:
    html_path = Path(artifacts["html_path"])
    tree_path = Path(artifacts["decision_tree_path"])
    report_html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
    tree_html = tree_path.read_text(encoding="utf-8", errors="replace") if tree_path.exists() else ""
    return report_html, tree_html


async def _enqueue_report_delivery_email(
    *,
    tenant_id: str,
    owner_user_id: str,
    recipient_email: str,
    report_id: str,
    incident_id: str,
    artifacts: dict,
    output_language: str = "",
    library_item_id: str = "",
) -> None:
    """Queue completion email when report artifacts are ready (idempotent)."""
    email = (recipient_email or "").strip()
    if (not email or "@" not in email) and "@" in (owner_user_id or ""):
        email = owner_user_id.strip()
    if not email or "@" not in email:
        print(f"⚠️  Report delivery skipped: no recipient email for {incident_id}")
        return
    lang = (output_language or "").strip()
    if not lang:
        try:
            incident = _require_incident_record(tenant_id, incident_id)
            lang = (incident.get("output_language") or "tr").strip()
        except Exception:
            lang = "tr"
    artifact_version = str(artifacts.get("generated_at") or incident_id).strip()
    try:
        await asyncio.to_thread(
            report_deliveries.maybe_enqueue_report_email,
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            recipient_email=email,
            report_id=report_id,
            incident_id=incident_id,
            artifact_version=artifact_version,
            output_language=lang,
            html_path=str(artifacts.get("html_path") or ""),
            docx_path=str(artifacts.get("docx_path") or ""),
            library_item_id=library_item_id,
        )
    except Exception as mail_exc:  # noqa: BLE001
        print(f"⚠️  Report delivery enqueue skipped: {mail_exc}")


@app.get("/api/v1/usage/summary")
async def usage_summary(tenant_id: TenantId, owner_user_id: OwnerUserId):
    """Dashboard: balance, limit, usage percent, AI question count."""
    data = await asyncio.to_thread(token_account.get_usage_summary, tenant_id, owner_user_id)
    return {"success": True, "data": data}


@app.get("/api/v1/usage/timeseries")
async def usage_timeseries(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    days: int = Query(7, ge=1, le=90),
):
    series = await asyncio.to_thread(token_account.get_timeseries, tenant_id, owner_user_id, days)
    return {"success": True, "data": {"days": days, "series": series}}


@app.get("/api/v1/usage/by-module")
async def usage_by_module(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    days: int = Query(30, ge=1, le=365),
):
    rows = await asyncio.to_thread(token_account.get_module_breakdown, tenant_id, owner_user_id, days)
    return {"success": True, "data": {"modules": rows}}


@app.get("/api/v1/usage/recent")
async def usage_recent(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    limit: int = Query(20, ge=1, le=100),
):
    rows = await asyncio.to_thread(token_account.get_recent_operations, tenant_id, owner_user_id, limit)
    return {"success": True, "data": {"operations": rows}}


@app.post("/api/v1/usage/top-up")
async def usage_top_up(tenant_id: TenantId, owner_user_id: OwnerUserId, body: TokenTopUpRequest):
    """Manual credit (v1 admin); target user defaults to caller."""
    target = (body.owner_user_id or owner_user_id).strip()
    amount = max(0, int(body.amount))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    acc = await asyncio.to_thread(token_account.top_up, tenant_id, target, amount)
    return {"success": True, "data": acc}


@app.get("/api/v1/library/status")
async def library_status():
    """Ops: where reports are stored and whether Mongo is reachable (no auth required)."""
    loc = saved_reports_store.store_location()
    ok, err = await asyncio.to_thread(saved_reports_store.ping_store)
    count = await asyncio.to_thread(saved_reports_store.count_all_documents)
    if ok:
        try:
            await asyncio.to_thread(saved_reports_store.ensure_collection)
        except Exception:  # noqa: BLE001
            pass
    return {
        "success": True,
        "data": {
            **loc,
            "ping_ok": ok,
            "ping_error": err or None,
            "document_count": count,
            "atlas_path": f"{loc.get('database')}.{loc.get('collection')}",
        },
    }


@app.get("/api/v1/library/items")
async def library_list_items(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    kind: Optional[str] = Query(None),
):
    """List saved drafts/reports for the authenticated user within the tenant."""
    try:
        items = saved_reports_store.list_items(tenant_id, owner_user_id, kind=kind)
        return {"success": True, "data": {"items": items}}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/library/items")
async def library_upsert_item(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    body: LibraryUpsertRequest,
):
    try:
        item = saved_reports_store.upsert_item(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            kind=body.kind,
            snapshot=body.snapshot or {},
            title_hint=body.title_hint or "",
            incident_id=body.incident_id or "",
            report_ready=body.report_ready,
            analysis_model_preset=body.analysis_model_preset or "",
            item_id=body.item_id or None,
        )
        return {"success": True, "data": item}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/v1/pricing/plans")
async def pricing_plans():
    """P0.11 — Public pricing catalog for admin panel."""
    return {"success": True, "data": load_pricing_catalog()}


@app.get("/api/v1/deliveries")
async def list_report_deliveries(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    limit: int = Query(20, ge=1, le=100),
):
    """P0.10 — Email delivery audit timeline for current user."""
    try:
        rows = await asyncio.to_thread(
            report_deliveries.list_deliveries, tenant_id, owner_user_id, limit=limit
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    from shared.email_sender import get_smtp_public_config

    return {
        "success": True,
        "data": {
            "deliveries": rows,
            "smtp": get_smtp_public_config(),
            "notify_default": report_deliveries.notify_enabled_for_user(tenant_id=tenant_id),
        },
    }


@app.get("/api/v1/reports/delivery/download")
async def report_delivery_download(token: str = Query(..., min_length=8)):
    """Signed, time-limited HTML or DOCX download (P0.10)."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or expired link")
    tenant_id = (payload.get("tenant_id") or "").strip()
    owner_user_id = (payload.get("owner_user_id") or "").strip()
    incident_id = (payload.get("incident_id") or "").strip()
    artifact = (payload.get("artifact") or "html").strip().lower()
    if not tenant_id or not owner_user_id or not incident_id:
        raise HTTPException(status_code=400, detail="Malformed token")
    incident = _require_incident_record(tenant_id, incident_id)
    artifacts = incident.get("report_artifacts") or {}
    if not _validate_artifact_paths(artifacts):
        artifacts = _generate_report_artifacts(tenant_id, incident_id)
    if artifact == "docx":
        path = Path(artifacts["docx_path"])
        if not path.exists():
            raise HTTPException(status_code=404, detail="DOCX not found")
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{incident_id}_report.docx",
        )
    path = Path(artifacts["html_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="HTML not found")
    return FileResponse(path, media_type="text/html; charset=utf-8", filename=f"{incident_id}_report.html")


@app.post("/api/v1/library/items/finalize")
async def library_finalize_report(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    body: LibraryFinalizeRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """
    After pipeline completes: upsert report row, generate HTML artifacts, store in Mongo for the user.
    """
    incident_id = (body.incident_id or "").strip()
    if not incident_id:
        raise HTTPException(status_code=400, detail="incident_id is required")
    try:
        item = saved_reports_store.upsert_item(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            kind="report",
            snapshot=body.snapshot or {},
            title_hint=body.title_hint or "",
            incident_id=incident_id,
            report_ready=False,
            analysis_model_preset=body.analysis_model_preset or "",
        )
        if body.report_layout:
            _apply_report_layout_to_incident(
                tenant_id,
                incident_id,
                body.report_layout,
                force_regenerate=True,
            )
        artifacts = _generate_report_artifacts(tenant_id, incident_id)
        report_html, tree_html = _read_artifact_files(artifacts)
        if not report_html:
            raise HTTPException(status_code=500, detail="Report HTML could not be read")
        updated = saved_reports_store.attach_artifacts(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            item_id=item["id"],
            report_html=report_html,
            decision_tree_html=tree_html,
        )
        await _enqueue_report_delivery_email(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            recipient_email=(x_user_email or "").strip(),
            report_id=str((updated or item).get("id") or incident_id),
            incident_id=incident_id,
            artifacts=artifacts,
            output_language=(body.snapshot or {}).get("output_language") or "",
            library_item_id=str((updated or item).get("id") or item.get("id") or ""),
        )
        return {"success": True, "data": updated or item}
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Finalize failed: {exc}") from exc


@app.get("/api/v1/library/items/{item_id}/artifact/{artifact_type}")
async def library_get_artifact(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    item_id: str,
    artifact_type: str,
):
    if artifact_type not in ("report", "decision_tree"):
        raise HTTPException(status_code=400, detail="artifact_type must be report or decision_tree")
    try:
        html = saved_reports_store.get_artifact_html(
            tenant_id, owner_user_id, item_id, artifact_type
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not html:
        raise HTTPException(status_code=404, detail="Artifact not found")
    filename = "report.html" if artifact_type == "report" else "decision_tree.html"
    return Response(
        content=html.encode("utf-8"),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@app.post("/api/v1/library/items/save-html")
async def library_save_html(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    body: LibrarySaveHtmlRequest,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """Store pre-generated HTML (avoids long-running finalize through serverless gateways)."""
    incident_id = (body.incident_id or "").strip()
    if not incident_id:
        raise HTTPException(status_code=400, detail="incident_id is required")
    if not (body.report_html or "").strip():
        raise HTTPException(status_code=400, detail="report_html is required")
    try:
        item = saved_reports_store.upsert_item(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            kind="report",
            snapshot=body.snapshot or {},
            title_hint=body.title_hint or "",
            incident_id=incident_id,
            report_ready=True,
            analysis_model_preset=body.analysis_model_preset or "",
        )
        updated = saved_reports_store.attach_artifacts(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            item_id=item["id"],
            report_html=body.report_html or "",
            decision_tree_html=body.decision_tree_html or "",
        )
        await _enqueue_report_delivery_email(
            tenant_id=tenant_id,
            owner_user_id=owner_user_id,
            recipient_email=(x_user_email or "").strip(),
            report_id=str((updated or item).get("id") or incident_id),
            incident_id=incident_id,
            artifacts={"generated_at": incident_id},
            output_language=(body.snapshot or {}).get("output_language") or "",
            library_item_id=str((updated or item).get("id") or item.get("id") or ""),
        )
        return {"success": True, "data": updated or item}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.delete("/api/v1/library/items/{item_id}")
async def library_delete_item(
    tenant_id: TenantId,
    owner_user_id: OwnerUserId,
    item_id: str,
):
    try:
        ok = saved_reports_store.delete_item(tenant_id, owner_user_id, item_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000
    )
