"""
V3.2 uçtan uca pipeline — analiz + rapor (INACTIVE, yerel test).

Production orchestrator bağlı değil.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .rootcause_agent_v3_2 import RootCauseAgentV3_2, create_v3_2_agent
from .skillbased_docx_agent_v3_2 import SkillBasedDocxAgentV32


def run_v3_2_analysis_and_report(
    part1_data: Dict,
    part2_data: Dict,
    investigation_data: Optional[Dict] = None,
    *,
    output_docx_path: str,
    use_rag: bool = False,
    progress_reporter: Any = None,
) -> Tuple[Dict, Dict]:
    """
    V3.2 kök neden analizi + HTML/DOCX rapor.

    Returns:
        (part3_rca_dict, report_content_dict)
    """
    agent = create_v3_2_agent(use_rag=use_rag)
    part3 = agent.analyze_root_causes(
        part1_data,
        part2_data,
        investigation_data,
        progress_reporter=progress_reporter,
    )

    raw_data = {
        "part1": part1_data,
        "part2": part2_data,
        "part3_rca": part3,
    }
    if investigation_data:
        raw_data.update({k: v for k, v in investigation_data.items() if k not in raw_data})

    docx_agent = SkillBasedDocxAgentV32()
    out_path = Path(output_docx_path)
    docx_agent.generate_report(raw_data, str(out_path.resolve()))
    return part3, raw_data


__all__ = [
    "RootCauseAgentV3_2",
    "SkillBasedDocxAgentV32",
    "run_v3_2_analysis_and_report",
]
