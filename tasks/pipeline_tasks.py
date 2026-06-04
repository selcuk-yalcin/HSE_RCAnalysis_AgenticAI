"""
Celery tasks for RCA + Action Plan pipeline.
"""

from __future__ import annotations

from typing import Any, Dict
import os

from celery_app import celery_app


def _transform_v2_to_frontend(part3_raw: dict) -> dict:
    immediate_causes = []
    underlying_causes = []
    root_causes = []

    for branch in part3_raw.get("analysis_branches", []):
        imm = branch.get("immediate_cause", {})
        if imm:
            immediate_causes.append(
                {
                    "code": imm.get("code", ""),
                    "category": imm.get("category_type", ""),
                    "description": imm.get("cause_tr", imm.get("cause", "")),
                    "evidence": imm.get("evidence_tr", ""),
                }
            )

        for why in branch.get("why_chain", []):
            underlying_causes.append(
                {
                    "level": why.get("level", 0),
                    "question": why.get("question_tr", ""),
                    "answer": why.get("answer_tr", ""),
                    "branch": branch.get("branch_number", 0),
                }
            )

        root = branch.get("root_cause", {})
        if root:
            root_causes.append(
                {
                    "code": root.get("code", ""),
                    "category": root.get("category_type", ""),
                    "description": root.get("cause_tr", root.get("cause", "")),
                    "explanation": root.get("explanation_tr", ""),
                    "branch": branch.get("branch_number", 0),
                }
            )

    return {
        "immediate_causes": immediate_causes,
        "underlying_causes": underlying_causes,
        "root_causes": root_causes,
        "analysis_method": part3_raw.get("analysis_method", "HSG245 Hierarchical 5-Why"),
        "incident_summary": part3_raw.get("incident_summary", ""),
        "final_report_tr": part3_raw.get("final_report_tr", ""),
        "_v2_raw": part3_raw,
    }


@celery_app.task(bind=True, name="pipeline.run_pipeline_task")
def run_pipeline_task(
    self,
    incident_id: str,
    part1_data: Dict[str, Any],
    part2_data: Dict[str, Any],
    investigation_payload: Dict[str, Any],
    tenant_id: str = "default",
    owner_user_id: str = "anonymous",
) -> Dict[str, Any]:
    from agents.actionplan_agent import ActionPlanAgent
    from agents.rootcause_agent_v2 import RootCauseAgentV2

    try:
        from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
        from agents.rca_cost_profile import root_cause_agent_kwargs

        use_rag = (os.getenv("ROOTCAUSE_USE_RAG") or "1").strip().lower() in ("1", "true", "yes", "on")
        rootcause_agent = RootCauseAgentV3_1(**root_cause_agent_kwargs(use_rag))
    except Exception:  # noqa: BLE001
        use_rag = (os.getenv("ROOTCAUSE_USE_RAG") or "1").strip().lower() in ("1", "true", "yes", "on")
        rootcause_agent = RootCauseAgentV2(use_rag=use_rag)

    actionplan_agent = ActionPlanAgent()

    from shared.pipeline_progress import celery_progress_reporter

    progress = celery_progress_reporter(self, incident_id, tenant_id)
    progress.emit(
        "Kök neden analizi başlatıldı",
        stage="investigate",
        progress=10,
        message="Kok neden analizi calisiyor",
    )

    inv = {
        "location": investigation_payload.get("location", ""),
        "who_involved": investigation_payload.get("who_involved", ""),
        "how_happened": investigation_payload.get("how_happened", ""),
        "activities": investigation_payload.get("activities", ""),
        "working_conditions": investigation_payload.get("working_conditions", ""),
        "safety_procedures": investigation_payload.get("safety_procedures", ""),
        "injuries": investigation_payload.get("injuries", ""),
        "why_probe_answers": investigation_payload.get("why_probe_answers", []) or [],
        "oracle_context": investigation_payload.get("oracle_context", ""),
        "output_language": investigation_payload.get("output_language", ""),
        "analysis_model_preset": investigation_payload.get("analysis_model_preset", ""),
    }

    analyze_kwargs = {}
    if hasattr(rootcause_agent, "analyze_root_causes"):
        import inspect

        sig = inspect.signature(rootcause_agent.analyze_root_causes)
        if "progress_reporter" in sig.parameters:
            analyze_kwargs["progress_reporter"] = progress

    part3_raw = rootcause_agent.analyze_root_causes(
        part1_data,
        part2_data,
        inv,
        **analyze_kwargs,
    )
    part3_data = _transform_v2_to_frontend(part3_raw)
    progress.emit(
        "RCA tamamlandı, aksiyon planı hazırlanıyor",
        stage="investigate",
        progress=55,
        message="RCA tamamlandi, aksiyon plani hazirlaniyor",
    )

    progress.emit(
        "Aksiyon planı oluşturuluyor",
        stage="actionplan",
        progress=62,
        message="Aksiyon plani olusturuluyor",
    )

    part4_data = actionplan_agent.generate_action_plan(
        {
            "root_causes": part3_data.get("root_causes", []),
            "underlying_causes": part3_data.get("underlying_causes", []),
            "immediate_causes": part3_data.get("immediate_causes", []),
            "severity": part2_data.get("investigation_level", ""),
        }
    )
    actionplan_meta = {
        "fallback_used": bool((part4_data or {}).get("_fallback")),
        "action_count": len((part4_data or {}).get("immediate_actions", []) or []),
    }
    progress.emit(
        "Action plan fallback used"
        if actionplan_meta["fallback_used"]
        else "Aksiyon planı oluşturuldu",
        stage="actionplan",
        progress=90,
        message=(
            "Action plan fallback used"
            if actionplan_meta["fallback_used"]
            else "Action plan generated"
        ),
    )

    result = {
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "owner_user_id": owner_user_id,
        "part3": part3_data,
        "part4": part4_data,
        "actionplan_meta": actionplan_meta,
        "stage": "completed",
        "progress": 100,
        "message": "Pipeline tamamlandi",
    }
    try:
        from shared import token_account

        job_id = str(getattr(self.request, "id", "") or "")
        token_account.debit_tokens(
            tenant_id,
            owner_user_id,
            amount=token_account.estimate_cost("pipeline"),
            reason="pipeline",
            module="deepwhy",
            incident_id=incident_id,
            job_id=job_id,
            operation_label=f"Kök neden pipeline ({incident_id})",
            idempotency_key=f"pipeline:{tenant_id}:{job_id}" if job_id else "",
        )
    except Exception:  # noqa: BLE001
        pass
    return result

