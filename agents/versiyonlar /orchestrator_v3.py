"""
Root Cause Orchestrator V3 - Hibrit Mod Dahil
=============================================

İKİ MOD:
    AUTO  → Mevcut tam otomatik akış (Part 1 → 2 → 3)
    HYBRID → Yeni hibrit akış (Part 1 → 2 → Uzman Röportajı → 3)

KULLANIM:
    # Otomatik mod (eski davranış)
    orchestrator = RootCauseOrchestrator(mode="auto")
    result = orchestrator.run_investigation(incident_data)

    # Hibrit mod (yeni - uzmanla interaktif)
    orchestrator = RootCauseOrchestrator(mode="hybrid")
    result = orchestrator.run_investigation(incident_data)
"""

from typing import Dict, Optional
from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent
from .rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
from .critic_agent import CriticAgent, MAX_REVISION_ATTEMPTS
from .hybrid_session_agent import HybridSessionAgent


class RootCauseOrchestrator:

    def __init__(self, mode: str = "auto"):
        """
        mode: "auto" | "hybrid"
        """
        print("\n" + "="*70)
        print(f"🚀 ROOT CAUSE INVESTIGATION SYSTEM")
        print(f"   Mod: {'🤖 TAM OTOMATİK' if mode == 'auto' else '🤝 HİBRİT (Uzman+AI)'}")
        print("="*70)

        self.mode = mode
        self.overview_agent = OverviewAgent()
        self.assessment_agent = AssessmentAgent()

        # Mod'a göre ajan seç
        if mode == "hybrid":
            self.hybrid_agent = HybridSessionAgent()
        else:
            self.rootcause_agent = RootCauseAgent()
            self.critic_agent = CriticAgent()

        self.investigation_data = {
            "part1": None,
            "part2": None,
            "part3_rca": None,
            "mode": mode,
            "status": "initialized"
        }

        print(f"✅ Tüm ajanlar hazır\n")

    def run_investigation(self, incident_data: Dict) -> Dict:
        try:
            # Part 1 — her iki modda da aynı
            print("\n📌 ADIM 1: Genel Bakış")
            self.investigation_data["part1"] = \
                self.overview_agent.process_initial_report(incident_data)

            # Part 2 — her iki modda da aynı
            print("\n📌 ADIM 2: Değerlendirme")
            self.investigation_data["part2"] = \
                self.assessment_agent.assess_incident(
                    self.investigation_data["part1"], incident_data
                )

            # Part 3 — mod'a göre ayrışır
            print("\n📌 ADIM 3: Kök Neden Analizi")

            if self.mode == "hybrid":
                # Hibrit mod: uzmanla interaktif
                raw_text = incident_data.get("description", "") + \
                           " " + incident_data.get("investigation_details", {}).get(
                               "how_happened", "")

                self.investigation_data["part3_rca"] = \
                    self.hybrid_agent.run_session(raw_text)
            else:
                # Otomatik mod: eleştirmen döngüsüyle
                self.investigation_data["part3_rca"] = \
                    self._run_auto_with_critique(incident_data)

            self.investigation_data["status"] = "complete"
            return self.investigation_data

        except Exception as e:
            print(f"\n❌ Hata: {e}")
            self.investigation_data["status"] = "error"
            raise

    def _run_auto_with_critique(self, incident_data: Dict) -> Dict:
        """Otomatik mod — eleştirmen döngüsü"""
        revision_count = 0
        best_rca = None
        best_score = 0.0

        while revision_count <= MAX_REVISION_ATTEMPTS:
            rca_data = self.rootcause_agent.analyze_root_causes(
                self.investigation_data["part1"],
                self.investigation_data["part2"],
                incident_data.get("investigation_details")
            )

            incident_summary = self._build_summary()
            critique = self.critic_agent.review_full_analysis(
                rca_data, incident_summary
            )

            score = critique.get("overall_score", 0.0)
            if score > best_score:
                best_score = score
                best_rca = rca_data
                best_rca["critic_review"] = critique

            if critique.get("overall_verdict") == "PASS":
                print(f"\n✅ Analiz onaylandı (Puan: {score}/10)")
                return rca_data

            revision_count += 1
            self.rootcause_agent.used_root_cause_codes = set()

        print(f"\n⚠️  Max revizyon aşıldı. En iyi sonuç kullanılıyor ({best_score}/10)")
        return best_rca

    def _build_summary(self) -> str:
        p1 = self.investigation_data.get("part1", {})
        brief = p1.get("brief_details", {})
        parts = [v for v in brief.values() if v] if isinstance(brief, dict) else []
        return ". ".join(parts) or "Özet yok"

    def get_investigation_data(self) -> Dict:
        return self.investigation_data

    def export_to_json(self, filepath: str):
        import json
        from pathlib import Path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.investigation_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Kaydedildi: {filepath}")
