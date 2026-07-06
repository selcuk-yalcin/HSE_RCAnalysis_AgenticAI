"""
SkillBasedDocxAgent V3.2 — rapor katmanı trainset why_chain ile uyumlu.

Orijinal skillbased_docx_agent.py değişmez; V3.2 pipeline bu sınıfı kullanır.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional

try:
    import agents.skillbased_docx_agent as _docx_mod
    from agents.skillbased_docx_agent import (
        CONTENT_SYSTEM_PROMPT,
        SkillBasedDocxAgent,
    )
except ImportError:
    import agents.skillbased_docx_agent as _docx_mod  # type: ignore[no-redef]
    from ..skillbased_docx_agent import (
        CONTENT_SYSTEM_PROMPT,
        SkillBasedDocxAgent,
    )

from .report_why_chain_v3_2 import pin_agent_why_chains_to_report_v32


# V3.1 prompt üzerine trainset W1 kuralı
CONTENT_SYSTEM_PROMPT_V32 = CONTENT_SYSTEM_PROMPT.replace(
    "- why_chain: Klasik 5-Why — NEDEN 1 olay sorusu (olay metninden), cevap doğrudan neden; "
    "NEDEN 2 doğrudan nedene \"Neden ...?\" sorusu; NEDEN 3–5 bir önceki cevabın alt nedeni. "
    "Olay özetini baştan sona tekrarlayan uzun soru yazma.",
    "- why_chain: BU ALANI YENİDEN YAZMA — boş bırak; sistem V3.2 agent part3_rca verisinden doldurur. "
    "NEDEN 1 = olay-zarar sorusu (ortak, örn. Garcia düşme yaralanması) + A/B cevap (evidence_tr); "
    "NEDEN 2 A/B mekanizmasına neden; NEDEN 3–5 agent zinciri → C/D kök.",
).replace(
    '{"number": 1, "question": "Neden [doğrudan neden kısa ifade]?", "answer": "Kısa olgu + gerekirse kısa açıklama", "code": "", "category": ""}',
    '{"number": 1, "question": "(sistem doldurur — trainset W1)", "answer": "", "code": "", "category": ""}',
)


class SkillBasedDocxAgentV32(SkillBasedDocxAgent):
    """
    Rapor üretimi — merge sonrası V3.2 agent why_chain pin.
    """

    AGENT_VERSION = "3.2"

    def _pin_agent_why_chains(self, content: Dict, raw_data: Dict) -> Dict:
        return pin_agent_why_chains_to_report_v32(content, raw_data)

    def _build_deterministic_fallback_content(
        self, raw_data: Dict, lang: Optional[Dict] = None
    ) -> Dict:
        """Fallback iskelet + V3.2 why_chain pin."""
        fb = super()._build_deterministic_fallback_content(raw_data, lang)
        return self._pin_agent_why_chains(fb, raw_data)

    def _generate_content_with_claude(self, raw_data: Dict, lang: Optional[Dict] = None) -> Dict:
        """LLM içerik + merge sonrası V3.2 why_chain pin."""
        original_prompt = _docx_mod.CONTENT_SYSTEM_PROMPT
        _docx_mod.CONTENT_SYSTEM_PROMPT = CONTENT_SYSTEM_PROMPT_V32
        try:
            content = super()._generate_content_with_claude(raw_data, lang)
        finally:
            _docx_mod.CONTENT_SYSTEM_PROMPT = original_prompt

        if isinstance(content, dict):
            return self._pin_agent_why_chains(content, raw_data)
        return content

    def _build_decision_tree(self, data: Dict, output_path: str) -> None:
        """V3.2 trainset W1 ile decision tree."""
        try:
            from .decision_tree_v3_2 import DecisionTreeGeneratorV32
        except ImportError:
            from agents.v3_2.decision_tree_v3_2 import DecisionTreeGeneratorV32

        try:
            rca_data = None
            incident_title = "Kaza Analizi"
            if "part3_rca" in data:
                rca_data = data["part3_rca"]
                if "part1" in data and "overview" in data["part1"]:
                    incident_title = data["part1"]["overview"].get("what_happened", incident_title)
            elif "analysis_branches" in data:
                rca_data = data
            if not rca_data:
                print("  Uyarı: RCA verisi bulunamadı, decision tree oluşturulamadı")
                return

            tree_payload = dict(rca_data) if isinstance(rca_data, dict) else {}
            part1 = data.get("part1") if isinstance(data.get("part1"), dict) else {}
            overview = part1.get("overview") if isinstance(part1.get("overview"), dict) else {}
            tree_payload["part1"] = part1
            try:
                from agents.report_text_sanitize import full_incident_narrative_for_tree
            except ImportError:
                from ..report_text_sanitize import full_incident_narrative_for_tree
            best_narrative = ""
            for src in (
                overview.get("what_happened"),
                part1.get("description"),
                tree_payload.get("incident_summary"),
                tree_payload.get("incident_event"),
            ):
                if isinstance(src, str) and src.strip():
                    prepared = full_incident_narrative_for_tree(src.strip())
                    if len(prepared) > len(best_narrative):
                        best_narrative = prepared
            if best_narrative:
                tree_payload["incident_summary"] = best_narrative

            gen = DecisionTreeGeneratorV32()
            gen.generate_html(
                rca_data=tree_payload,
                output_path=output_path,
                incident_title=incident_title,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  Uyarı: Decision tree v3.2: {exc}")
            super()._build_decision_tree(data, output_path)
