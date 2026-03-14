"""
Root Cause Orchestrator V3 - Vector Search Entegrasyonu
=========================================================

DEĞİŞİKLİKLER (orchestrator.py → orchestrator_v3.py):
  ✅ Tüm agent'lar aynı şekilde çalışıyor
  ➕ RootCauseAgentV3 kullanıyor (vector search destekli)
  ➕ Vector search aktif/pasif toggle (.env: USE_VECTOR_SEARCH)

NOT: Bu dosya V3 test ortamı içindir. Orijinal orchestrator.py değiştirilmemiştir.
"""

from typing import Dict, Optional
import sys
import os

# V3 klasöründen parent klasöre bak
v3_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(v3_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Orijinal agent'ları import et
try:
    from overview_agent import OverviewAgent
except ImportError:
    from agents.overview_agent import OverviewAgent

try:
    from assessment_agent import AssessmentAgent
except ImportError:
    from agents.assessment_agent import AssessmentAgent

try:
    from skillbased_docx_agent import SkillBasedDocxAgent
except ImportError:
    try:
        from agents.skillbased_docx_agent import SkillBasedDocxAgent
    except ImportError:
        SkillBasedDocxAgent = None

# V3: RootCauseAgentV3'ü import et
try:
    from rootcause_agent_v3 import RootCauseAgentV3 as RootCauseAgent
    USING_V3 = True
except ImportError:
    # Fallback: V2
    try:
        from rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
    except ImportError:
        from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
    USING_V3 = False


class RootCauseOrchestratorV3:
    """
    HSG245 soruşturma iş akışı koordinatörü (V3 - Vector Enhanced)
    
    Adımlar:
    1. Overview Agent  → Part 1
    2. Assessment Agent → Part 2
    3. Root Cause Agent V3 → Part 3 (JSON + Vector Search)
    4. SkillBasedDocxAgent → DOCX Rapor
    """

    def __init__(self):
        print("\n" + "=" * 80)
        print("🚀 ROOT CAUSE INVESTIGATION SYSTEM V3 BAŞLATILIYOR")
        print("=" * 80)

        # Vector search durumu
        use_vector = os.getenv("USE_VECTOR_SEARCH", "false").lower() == "true"
        
        if USING_V3:
            print(f"\n✅ RootCauseAgentV3 aktif")
            print(f"   Vector Search: {'🟢 Aktif' if use_vector else '🔴 Pasif (Dictionary)'}")
        else:
            print(f"\n⚠️  RootCauseAgentV2 kullanılıyor (fallback)")

        self.overview_agent = OverviewAgent()
        self.assessment_agent = AssessmentAgent()
        self.rootcause_agent = RootCauseAgent()

        # DOCX Rapor Ajanı
        if SkillBasedDocxAgent:
            try:
                self.docx_agent = SkillBasedDocxAgent()
                self._docx_enabled = True
            except ValueError as e:
                print(f"⚠️  DOCX Agent devre dışı: {e}")
                print("   ANTHROPIC_API_KEY ayarlanınca otomatik etkinleşir.")
                self._docx_enabled = False
        else:
            print("⚠️  SkillBasedDocxAgent import edilemedi")
            self._docx_enabled = False

        self.investigation_data = {
            "part1": None,
            "part2": None,
            "part3_rca": None,
            "docx_report": None,
            "status": "initialized",
            "version": "V3 - Vector Enhanced" if USING_V3 else "V2 - Fallback"
        }

        print("\n✅ Tüm ajanlar başlatıldı")
        print("=" * 80)

    def run_investigation(self, incident_data: Dict) -> Dict:
        """
        Tam soruşturma iş akışını çalıştırır (V3).
        
        Args:
            incident_data: Olay bilgileri
            
        Returns:
            Tam soruşturma sonuçları (DOCX rapor yolu dahil)
        """
        print("\n" + "=" * 80)
        print("🔬 SORUŞTURMA BAŞLIYOR (V3)")
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

            # Adım 3: Part 3 — Kök Neden Analizi (V3 - Vector Enhanced)
            print("\n📌 ADIM 3/4: Kök Neden Analizi (Part 3 - V3)")
            print("-" * 80)
            self.investigation_data["part3_rca"] = self.rootcause_agent.analyze_root_causes(
                self.investigation_data["part1"],
                self.investigation_data["part2"],
                incident_data.get("investigation_details"),
            )
            self.investigation_data["status"] = "part3_complete"

            # Adım 4 — DOCX Rapor Üretimi
            if self._docx_enabled:
                print("\n📌 ADIM 4/4: DOCX Rapor Üretimi (Claude API)")
                print("-" * 80)

                ref_no = self.investigation_data["part1"].get("ref_no", "report")
                output_path = f"outputs/{ref_no}_hse_report_v3.docx"

                report_path = self.docx_agent.generate_report(
                    investigation_data=self.investigation_data,
                    output_path=output_path,
                )
                self.investigation_data["docx_report"] = report_path
                self.investigation_data["status"] = "investigation_complete"
            else:
                print("\n⚠️  ADIM 4/4: DOCX raporu atlandı (API key eksik)")
                self.investigation_data["status"] = "investigation_complete_no_docx"

            self._print_final_summary()
            return self.investigation_data

        except Exception as e:
            print(f"\n❌ Soruşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            
            self.investigation_data["status"] = "error"
            self.investigation_data["error"] = str(e)
            raise

    def _print_final_summary(self):
        print("\n" + "=" * 80)
        print("✅ SORUŞTURMA TAMAMLANDI (V3)")
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

        # Root causes listesi
        print(f"\n🎯 Kök Nedenler:")
        for i, rc in enumerate(root_causes, 1):
            code = rc.get('code', '???')
            title = rc.get('standard_title_tr', '')
            cause = rc.get('cause_tr', '')
            
            if title:
                print(f"   {i}. [{code}] {title}")
            else:
                print(f"   {i}. [{code}] {cause[:80]}...")

        docx = self.investigation_data.get("docx_report")
        if docx:
            print(f"\n📄 DOCX Raporu:       {docx}")
        else:
            print("\n📄 DOCX Raporu:       Üretilmedi (ANTHROPIC_API_KEY eksik)")

        version = self.investigation_data.get('version', 'Unknown')
        print(f"\n🔧 Versiyon:          {version}")
        print(f"✅ Durum:             {self.investigation_data.get('status', 'Bilinmiyor')}")
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


# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ORCHESTRATOR V3 - STANDALONE TEST" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Test incident
    test_incident = {
        "description": """
        Tarih: 15 Ocak 2024
        Lokasyon: Rafineri ünitesi, yüksek basınç tesisatı bakım alanı
        
        OLAY:
        Bakım teknisyeni, yüksek basınç tesisatında sızıntı kontrolü yaparken,
        sistemi izole etmeden (LOTO prosedürü uygulamadan) vananın altındaki
        flanşı gevşetmeye başladı. Sistem hala basınçlı olduğu için, flanj 
        çözüldüğünde ani basınç boşalması meydana geldi ve kimyasal sıvı fışkırdı.
        
        Teknisyen, bu işlemi daha önce "hızlı iş" olarak 4-5 kez yapmıştı ve 
        hiç sorun çıkmamıştı. Vardiya amiri, sahada bulunmuyordu ve bu tip 
        kestirme yöntemlerin kullanıldığından habersizdi.
        
        Şirketin LOTO prosedürü yazılı olarak mevcuttu ancak son 1 yılda hiç 
        denetim yapılmamıştı. Bakım ekibi, prosedürlerin "fazla zaman aldığını" 
        düşünüyor ve rutin işlerde atlamayı normal karşılıyordu.
        
        SONUÇ:
        Teknisyenin yüzüne ve vücuduna kimyasal sıçradı. İkinci derece yanık 
        ve göz tahrişi. 2 hafta iş göremez durumda.
        """,
        "incident_type": "Chemical Exposure",
        "date": "2024-01-15",
        "location": "Refinery - High Pressure Unit"
    }
    
    # Orchestrator'ı başlat
    orchestrator = RootCauseOrchestratorV3()
    
    # Soruşturma yap
    try:
        result = orchestrator.run_investigation(test_incident)
        
        # JSON export
        json_path = "outputs/v3_test_investigation.json"
        orchestrator.export_to_json(json_path)
        
        print("\n\n🎉 Test tamamlandı!")
        print(f"📄 JSON: {json_path}")
        
        if result.get("docx_report"):
            print(f"📄 DOCX: {result['docx_report']}")
        
    except Exception as e:
        print(f"\n❌ Test başarısız: {e}")
        import traceback
        traceback.print_exc()
