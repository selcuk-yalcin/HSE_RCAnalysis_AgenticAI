"""
Celery tasks for RCA + Action Plan pipeline.
"""

from __future__ import annotations

from typing import Any, Dict

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
) -> Dict[str, Any]:
    from agents.actionplan_agent import ActionPlanAgent
    from agents.rootcause_agent_v2 import RootCauseAgentV2

    try:
        from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1

        rootcause_agent = RootCauseAgentV3_1(use_rag=False)
    except Exception:  # noqa: BLE001
        rootcause_agent = RootCauseAgentV2(use_rag=False)

    actionplan_agent = ActionPlanAgent()

    self.update_state(
        state="PROGRESS",
        meta={
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "stage": "investigate",
            "progress": 20,
            "message": "Kok neden analizi calisiyor",
        },
    )
    # Cooperative checkpoint to keep state updates flowing on long RCA runs.
    self.update_state(
        state="PROGRESS",
        meta={
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "stage": "investigate",
            "progress": 30,
            "message": "RCA branch generation in progress",
        },
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
    }

    part3_raw = rootcause_agent.analyze_root_causes(
        part1_data,
        part2_data,
        inv,
    )
    part3_data = _transform_v2_to_frontend(part3_raw)
    self.update_state(
        state="PROGRESS",
        meta={
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "stage": "investigate",
            "progress": 60,
            "message": "RCA completed, preparing action plan",
        },
    )

    self.update_state(
        state="PROGRESS",
        meta={
            "incident_id": incident_id,
            "tenant_id": tenant_id,
            "stage": "actionplan",
            "progress": 75,
            "message": "Aksiyon plani olusturuluyor",
        },
    )

    part4_data = actionplan_agent.generate_action_plan(
        {
            "root_causes": part3_data.get("root_causes", []),
            "underlying_causes": part3_data.get("underlying_causes", []),
            "immediate_causes": part3_data.get("immediate_causes", []),
            "severity": part2_data.get("investigation_level", ""),
        }
    )

    return {
        "tenant_id": tenant_id,
        "incident_id": incident_id,
        "part3": part3_data,
        "part4": part4_data,
        "stage": "completed",
        "progress": 100,
        "message": "Pipeline tamamlandi",
    }

