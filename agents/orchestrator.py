"""
Root Cause Orchestrator - DOCX Raporu ile Güncellenmiş Versiyon
================================================================

DEĞİŞİKLİKLER (orijinal orchestrator.py'a göre):
  + SkillBasedDocxAgent import edildi
  + __init__ içinde docx_agent başlatılıyor
  + run_investigation() sonunda DOCX raporu otomatik üretiliyor
  + investigation_data["docx_report"] alanı eklendi
"""

from typing import Dict, Optional
from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent
from .rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent

# ── YENİ IMPORT ────────────────────────────────────────────────────────────────
from .skillbased_docx_agent import SkillBasedDocxAgent
# ──────────────────────────────────────────────────────────────────────────────


class RootCauseOrchestrator:
    """
    HSG245 soruşturma iş akışı koordinatörü
    
    Adımlar:
    1. Overview Agent  → Part 1
    2. Assessment Agent → Part 2
    3. Root Cause Agent → Part 3 (JSON)
    4. SkillBasedDocxAgent → DOCX Rapor  ← YENİ
    """

    def __init__(self):
        print("\n" + "=" * 80)
        print("🚀 ROOT CAUSE INVESTIGATION SYSTEM BAŞLATILIYOR")
        print("=" * 80)

        self.overview_agent = OverviewAgent()
        self.assessment_agent = AssessmentAgent()
        self.rootcause_agent = RootCauseAgent()

        # ── YENİ: DOCX Rapor Ajanı ────────────────────────────────────────────
        # ANTHROPIC_API_KEY env var'dan otomatik okunur
        # .env dosyanıza ekleyin: ANTHROPIC_API_KEY=sk-ant-...
        try:
            self.docx_agent = SkillBasedDocxAgent()
            self._docx_enabled = True
        except ValueError as e:
            print(f"⚠️  DOCX Agent devre dışı: {e}")
            print("   ANTHROPIC_API_KEY ayarlanınca otomatik etkinleşir.")
            self._docx_enabled = False
        # ──────────────────────────────────────────────────────────────────────

        self.investigation_data = {
            "part1": None,
            "part2": None,
            "part3_rca": None,
            "docx_report": None,   # ← YENİ
            "status": "initialized",
        }

        print("\n✅ Tüm ajanlar başlatıldı")
        print("=" * 80)

    def run_investigation(self, incident_data: Dict) -> Dict:
        """
        Tam soruşturma iş akışını çalıştırır.
        
        Args:
            incident_data: Olay bilgileri
            
        Returns:
            Tam soruşturma sonuçları (DOCX rapor yolu dahil)
        """
        print("\n" + "=" * 80)
        print("🔬 SORUŞTURMA BAŞLIYOR")
        print("=" * 80)

        try:
            # Adım 1: Part 1 — Genel Bakış
            print("\n📌 ADIM 1/4: Genel Bakış (Part 1)")
            print("-" * 80)
            self.investigation_data["part1"] = self.overview_agent.process_initial_report(
                incident_data
            )
            self.investigation_data["status"] = "part1_complete"

            # Adım 2: Part 2 — Değerlendirme
            print("\n📌 ADIM 2/4: Değerlendirme (Part 2)")
            print("-" * 80)
            self.investigation_data["part2"] = self.assessment_agent.assess_incident(
                self.investigation_data["part1"], incident_data
            )
            self.investigation_data["status"] = "part2_complete"

            # Adım 3: Part 3 — Kök Neden Analizi
            print("\n📌 ADIM 3/4: Kök Neden Analizi (Part 3)")
            print("-" * 80)
            self.investigation_data["part3_rca"] = self.rootcause_agent.analyze_root_causes(
                self.investigation_data["part1"],
                self.investigation_data["part2"],
                incident_data.get("investigation_details"),
            )
            self.investigation_data["status"] = "part3_complete"

            # ── YENİ: Adım 4 — DOCX Rapor Üretimi ────────────────────────────
            if self._docx_enabled:
                print("\n📌 ADIM 4/4: DOCX Rapor Üretimi (Claude API)")
                print("-" * 80)

                ref_no = self.investigation_data["part1"].get("ref_no", "report")
                output_path = f"outputs/{ref_no}_hse_report.docx"

                report_path = self.docx_agent.generate_report(
                    investigation_data=self.investigation_data,
                    output_path=output_path,
                )
                self.investigation_data["docx_report"] = report_path
                self.investigation_data["status"] = "investigation_complete"
            else:
                print("\n⚠️  ADIM 4/4: DOCX raporu atlandı (API key eksik)")
                self.investigation_data["status"] = "investigation_complete_no_docx"
            # ──────────────────────────────────────────────────────────────────

            self._print_final_summary()
            return self.investigation_data

        except Exception as e:
            print(f"\n❌ Soruşturma hatası: {e}")
            self.investigation_data["status"] = "error"
            self.investigation_data["error"] = str(e)
            raise

    def _print_final_summary(self):
        print("\n" + "=" * 80)
        print("✅ SORUŞTURMA TAMAMLANDI")
        print("=" * 80)

        p1 = self.investigation_data.get("part1", {})
        p2 = self.investigation_data.get("part2", {})
        p3 = self.investigation_data.get("part3_rca", {})

        print(f"\n📋 Referans No:       {p1.get('ref_no', 'N/A')}")
        print(f"📊 Olay Tipi:         {p1.get('incident_type', 'N/A')}")
        print(f"⚠️  Şiddet:           {p2.get('actual_potential_harm', 'N/A')}")
        print(f"🔍 Soruşturma Düzeyi: {p2.get('investigation_level', 'N/A')}")
        print(f"📝 RIDDOR:            {p2.get('riddor_reportable', 'N/A')}")

        branches = p3.get("analysis_branches", [])
        root_causes = p3.get("final_root_causes", [])
        print(f"\n🎯 Analiz Dalı Sayısı: {len(branches)}")
        print(f"   Kök Neden Sayısı:   {len(root_causes)}")

        docx = self.investigation_data.get("docx_report")
        if docx:
            print(f"\n📄 DOCX Raporu:       {docx}")
        else:
            print("\n📄 DOCX Raporu:       Üretilmedi (ANTHROPIC_API_KEY eksik)")

        print(f"\n✅ Durum: {self.investigation_data.get('status', 'Bilinmiyor')}")
        print("=" * 80)

    def get_investigation_data(self) -> Dict:
        return self.investigation_data

    def export_to_json(self, filepath: str):
        import json
        from pathlib import Path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.investigation_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Soruşturma dışa aktarıldı: {filepath}")
