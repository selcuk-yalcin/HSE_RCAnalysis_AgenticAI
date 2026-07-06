"""
V3.2 Decision Tree — trainset W1 sorusu (build_event_why1 yerine).
"""

from __future__ import annotations

try:
    from agents.decision_tree_mermaid import DecisionTreeGenerator
except ImportError:
    from ..decision_tree_mermaid import DecisionTreeGenerator

from .why_chain_quality_v3_2 import build_trainset_why1_question_heuristic


class DecisionTreeGeneratorV32(DecisionTreeGenerator):
    """5-Why ağacında NEDEN 1 = trainset tarzı olay sorusu."""

    def _build_first_why_question(self, incident_summary: str) -> str:
        return build_trainset_why1_question_heuristic(incident_summary)
