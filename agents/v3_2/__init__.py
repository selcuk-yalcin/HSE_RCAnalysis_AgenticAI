"""
V3.2 — trainset tarzı 5-Why agent paketi (INACTIVE).

Lazy import — ağır modüller yalnızca kullanıldığında yüklenir.
"""

from typing import Any

__all__ = [
    "RootCauseAgentV3_2",
    "WhyChainV32",
    "SkillBasedDocxAgentV32",
    "DecisionTreeGeneratorV32",
    "create_v3_2_agent",
    "check_v3_2_status",
    "run_v3_2_analysis_and_report",
    "build_trainset_why1_question",
    "build_trainset_why1_question_heuristic",
    "immediate_cause_ab_answer",
    "pin_agent_why_chains_to_report_v32",
]


def __getattr__(name: str) -> Any:
    if name in (
        "build_trainset_why1_question",
        "build_trainset_why1_question_heuristic",
        "immediate_cause_ab_answer",
    ):
        from .why_chain_quality_v3_2 import (
            build_trainset_why1_question,
            build_trainset_why1_question_heuristic,
            immediate_cause_ab_answer,
        )

        return {
            "build_trainset_why1_question": build_trainset_why1_question,
            "build_trainset_why1_question_heuristic": build_trainset_why1_question_heuristic,
            "immediate_cause_ab_answer": immediate_cause_ab_answer,
        }[name]
    if name == "WhyChainV32":
        from .why_chain_v3_2 import WhyChainV32

        return WhyChainV32
    if name == "RootCauseAgentV3_2":
        from .rootcause_agent_v3_2 import RootCauseAgentV3_2

        return RootCauseAgentV3_2
    if name == "create_v3_2_agent":
        from .rootcause_agent_v3_2 import create_v3_2_agent

        return create_v3_2_agent
    if name == "check_v3_2_status":
        from .rootcause_agent_v3_2 import check_v3_2_status

        return check_v3_2_status
    if name == "SkillBasedDocxAgentV32":
        from .skillbased_docx_agent_v3_2 import SkillBasedDocxAgentV32

        return SkillBasedDocxAgentV32
    if name == "DecisionTreeGeneratorV32":
        from .decision_tree_v3_2 import DecisionTreeGeneratorV32

        return DecisionTreeGeneratorV32
    if name == "pin_agent_why_chains_to_report_v32":
        from .report_why_chain_v3_2 import pin_agent_why_chains_to_report_v32

        return pin_agent_why_chains_to_report_v32
    if name == "run_v3_2_analysis_and_report":
        from .pipeline_v3_2 import run_v3_2_analysis_and_report

        return run_v3_2_analysis_and_report
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
