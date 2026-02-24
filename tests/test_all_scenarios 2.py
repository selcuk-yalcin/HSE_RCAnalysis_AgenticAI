#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSE ROOT CAUSE ANALYSIS - COMPREHENSIVE TEST SUITE
===================================================

Bu dosya 3 farklı HSE olay senaryosunu test eder:
1. Yüksekten Düşme (Fall from Height) - İskele güvenliği
2. Elektrik Çarpması (Electrical Shock) - LOTO prosedürü
3. Makine Sıkışması (Machine Entrapment) - Makine güvenliği

Her test:
- OverviewAgent → AssessmentAgent → RootCauseAgentV2 → SkillBasedDocxAgent
- JSON + DOCX + HTML çıktı üretir
- Prompt caching ile maliyet optimize edilir

Kullanım:
    python test_all_scenarios.py              # Tüm senaryolar
    python test_all_scenarios.py --fall       # Sadece düşme
    python test_all_scenarios.py --electrical # Sadece elektrik
    python test_all_scenarios.py --machine    # Sadece makine
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# INCIDENT DATA - 3 SCENARIOS
# ============================================================================

INCIDENT_FALL_FROM_HEIGHT = """
OLAY RAPORU - YÜKSEKTEN DÜŞME

Tarih: 18 Şubat 2026, Saat: 10:35
Lokasyon: Yapı İnşaat Şantiyesi - 4. Kat İskele Alanı
Rapor Eden: Şantiye Güvenlik Sorumlusu - Mehmet Kaya

OLAY AÇIKLAMASI:
İşçi Hasan Yıldız (32), iskele montaj işçisi, yaklaşık 6 metre yükseklikteki 
iskeleden düşerek zemine çakıldı. İşçi şu anda yoğun bakımda, durumu kritik.

YARALANMA DETAYLARI:
- L2 omurga vertebra kırığı
- Pelvis çatlağı (sağ taraf)
- İç kanama
- Yoğun bakım - entübe

GÜVENLİK DURUMU:
✗ Emniyet kemeri takılı DEĞİLDİ
✗ İskele korkuluğu EKSIK (montaj tamamlanmamış)
✗ Güvenlik ağı YOK
✓ Baret takılıydı
✓ İş ayakkabısı giyiliydi

OLAY ÖNCESİ KOŞULLAR:
- Proje 3 hafta gecikmeli, yönetim "hızlı bitirin" talimatı vermiş
- İskele montajı %80 tamamlanmış, korkuluk takılmamış
- Güvenlik eğitimi kayıtları eksik
- İşçi 2 ay önce işe başlamış, yüksekte çalışma eğitimi yok

TANIKLARIN İFADELERİ:
- Formen: "Herkes öyle yapıyor, kimse kemer takmıyor"
- Diğer işçi: "Korkuluk olmadan çalışmamız istendi, proje geç"
"""

INCIDENT_ELECTRICAL_SHOCK = """
OLAY RAPORU - ELEKTRİK ÇARPMASI

Tarih: 20 Şubat 2026, Saat: 15:20
Lokasyon: Üretim Tesisi - Ana Elektrik Panosu (MDB-02)
Rapor Eden: Elektrik Bakım Sorumlusu - İbrahim Aydın

OLAY AÇIKLAMASI:
Bakım teknisyeni Kemal Arslan (29), elektrik panosunda 380V akımına kapıldı.
Kardiyak arrest yaşadı (30 saniye), sonra defibrilatör ile canlandırıldı.

YARALANMA DETAYLARI:
- Kardiyak arrest (30 saniye sürdü)
- 2. derece yanıklar (sağ el ve kol)
- Kas hasarı
- Yoğun bakımda 2 gün kaldı
- Tahmini 3 ay tam iyileşme süresi

GÜVENLİK İHLALLERİ:
✗ LOTO (Lockout/Tagout) prosedürü UYGULANMADI
✗ Enerji kaynağı KESİLMEDİ (380V açık)
✗ Test cihazı KULLANILMADI (voltaj testi yapılmadı)
✗ Gözlemci YOK (tek başına çalışma)
✗ İzolasyon kilidi YOK
✗ Uyarı etiketi ASILMADI
✓ Elektrik eldiveni vardı (ancak KULLANMADI)
✓ Yalıtımlı ayakkabı giyiliydi

OLAY ÖNCESİ KOŞULLAR:
- Arıza acil, üretim durdu
- Vardiya lideri: "Hemen çöz, üretim durmasın"
- LOTO ekipmanı dolabında, ancak alınmadı
- Teknisyen LOTO eğitimi almamış
- Son 2 yılda 3 benzer "near-miss" olayı kaydedilmiş

KÜLTÜREL FAKTÖRLER:
- "Üretimi durdurmayalım" baskısı yaygın
- LOTO atlamak "normalize" olmuş
- Yönetim LOTO ihlallerini uyarmıyor
"""

INCIDENT_MACHINE_ENTRAPMENT = """
OLAY RAPORU - MAKİNE SIKIŞMASI

Tarih: 20 Şubat 2026, Saat: 08:45
Lokasyon: Paketleme Hattı - Konveyör Band Sistemi (KB-05)
Rapor Eden: Paketleme Vardiya Sorumlusu - Fatma Demir

OLAY AÇIKLAMASI:
Konveyör band operatörü Fatma Yılmaz (27), sağ eli konveyör bantla tambur 
arasında sıkıştı. 3 parmağında ezilme ve açık kırık meydana geldi.

YARALANMA DETAYLARI:
- İşaret parmağı: Açık kırık, eklem hasarı
- Orta parmak: Ezilme, yumuşak doku hasarı
- Yüzük parmağı: Kapalı kırık
- Acil ameliyat gerekti
- 4 ay iş göremezlik tahmini

GÜVENLİK İHLALLERİ:
✗ Makine ÇALIŞIRKEN müdahale edildi
✗ Koruyucu/guard ÇIKARILMIŞ (daha önce sökülmüş)
✗ Işık perdesi (light curtain) YOK
✗ Acil stop düğmesi ERİŞİMSİZ (karton yığınının arkasında)
✗ İki el kumanda sistemi YOK
✓ Eldiven takılıydı (ancak yardımcı olmadı)
✓ Saç topluydu

OLAY ÖNCESİ KOŞULLAR:
- Konveyör bant KRONIK ARIZALI (haftada 3-4 kez karton sıkışması)
- Guard 6 ay önce "erişim kolaylığı" için sökülmüş
- Vardiya lideri guard eksikliğinden haberdar
- Bakım talebi yapılmış ama öncelik verilmemiş
- Operatör 8 aydır aynı makinede çalışıyor
- "Çalışan makineye müdahale etme" kuralı VARDı ama uygulanmadı

KÜLTÜREL SORUNLAR:
- Guard sökme "yaygınlaşmış" (5 makinede daha aynı durum)
- Bakım ekibi yetersiz kaynak (2 kişi, 50+ makine)
- Üretim hedefleri agresif, duruş kabul edilmiyor
- Risk değerlendirmesi 3 yıl önce yapılmış, güncellenmemiş
"""


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_banner(text: str, char: str = "="):
    """Print a centered banner."""
    width = 80
    print(f"\n{char * width}")
    lines = text.split('\n')
    for line in lines:
        padding = (width - len(line)) // 2
        print(f"{' ' * padding}{line}")
    print(f"{char * width}\n")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")


def print_success(msg: str):
    """Print success message."""
    print(f"  ✅ {msg}")


def print_error(msg: str):
    """Print error message."""
    print(f"  ❌ {msg}")


def print_info(msg: str):
    """Print info message."""
    print(f"     {msg}")


def print_result_summary(results: Dict):
    """Print test result summary."""
    print_section("TEST SONUÇ ÖZETİ")
    
    total = len(results["steps"])
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    
    print(f"  Toplam Adım: {total}")
    print(f"  Başarılı: {passed}")
    print(f"  Başarısız: {total - passed}")
    
    print("\n  Adım Detayları:")
    for step, status in results["steps"].items():
        icon = "✅" if status == "PASSED" else "❌"
        print(f"    {icon} {step}: {status}")
    
    if results.get("files"):
        print("\n  Oluşturulan Dosyalar:")
        for f in results["files"]:
            file_path = Path(f)
            if file_path.exists():
                size = file_path.stat().st_size / 1024  # KB
                print(f"    📄 {f} ({size:.1f} KB)")
    
    duration = results.get("duration", 0)
    print(f"\n  Toplam Süre: {duration:.1f} saniye")
    
    return passed == total


# ============================================================================
# TEST SCENARIO CLASS
# ============================================================================

class ScenarioTest:
    """Base class for scenario testing."""
    
    def __init__(self, name: str, incident_data: str):
        self.name = name
        self.incident_data = incident_data
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "scenario": name,
            "timestamp": self.timestamp,
            "steps": {},
            "files": [],
            "start_time": time.time()
        }
    
    def run(self) -> Dict:
        """Run the full test scenario."""
        print_banner(f"TEST SENARYOSU: {self.name}")
        print_info(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Environment check
            self._check_environment()
            
            # Step 1: OverviewAgent
            part1 = self._run_overview()
            
            # Step 2: AssessmentAgent
            part2 = self._run_assessment(part1)
            
            # Step 3: RootCauseAgentV2
            part3 = self._run_rca(part1, part2)
            
            # Step 4: SkillBasedDocxAgent
            self._run_docx_generation(part1, part2, part3)
            
            # Calculate duration
            self.results["duration"] = time.time() - self.results["start_time"]
            
            # Print summary
            success = print_result_summary(self.results)
            
            return {
                "success": success,
                "results": self.results
            }
            
        except Exception as e:
            print_error(f"Test başarısız: {e}")
            import traceback
            traceback.print_exc()
            self.results["error"] = str(e)
            self.results["duration"] = time.time() - self.results["start_time"]
            return {
                "success": False,
                "results": self.results
            }
    
    def _check_environment(self):
        """Check environment and dependencies."""
        print_section("ADIM 1: Ortam Kontrolü")
        
        try:
            # API Key check
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY bulunamadı")
            print_success(f"API Key: {api_key[:12]}...{api_key[-4:]}")
            
            # Output directory
            Path("outputs").mkdir(exist_ok=True)
            print_success("Çıktı dizini hazır")
            
            self.results["steps"]["environment"] = "PASSED"
            
        except Exception as e:
            print_error(f"Ortam hatası: {e}")
            self.results["steps"]["environment"] = "FAILED"
            raise
    
    def _run_overview(self) -> Dict:
        """Run OverviewAgent."""
        print_section("ADIM 2: OverviewAgent")
        
        try:
            agent = OverviewAgent()
            print_success("Agent başlatıldı")
            
            incident_dict = {"description": self.incident_data}
            part1 = agent.process_initial_report(incident_dict)
            
            print_success(f"Ref No: {part1.get('ref_no')}")
            print_success(f"Olay Tipi: {part1.get('incident_type')}")
            
            self.results["steps"]["overview"] = "PASSED"
            self.results["part1"] = part1
            
            return part1
            
        except Exception as e:
            print_error(f"Hata: {e}")
            self.results["steps"]["overview"] = "FAILED"
            raise
    
    def _run_assessment(self, part1: Dict) -> Dict:
        """Run AssessmentAgent."""
        print_section("ADIM 3: AssessmentAgent")
        
        try:
            agent = AssessmentAgent()
            print_success("Agent başlatıldı")
            
            incident_dict = {"description": self.incident_data}
            part2 = agent.assess_incident(part1, incident_dict)
            
            print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
            print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
            print_success(f"Level: {part2.get('investigation', {}).get('level')}")
            
            self.results["steps"]["assessment"] = "PASSED"
            self.results["part2"] = part2
            
            return part2
            
        except Exception as e:
            print_error(f"Hata: {e}")
            self.results["steps"]["assessment"] = "FAILED"
            raise
    
    def _run_rca(self, part1: Dict, part2: Dict) -> Dict:
        """Run RootCauseAgentV2."""
        print_section("ADIM 4: RootCauseAgentV2")
        
        try:
            agent = RootCauseAgentV2()
            print_success("Agent başlatıldı")
            
            part3 = agent.analyze_root_causes(
                part1_data=part1,
                part2_data=part2,
                investigation_data={"description": self.incident_data}
            )
            
            branches = part3.get("analysis_branches", [])
            causes = part3.get("final_root_causes", [])
            
            print_success(f"Dallar: {len(branches)}")
            print_success(f"Kök nedenler: {len(causes)}")
            
            for i, rc in enumerate(causes, 1):
                code = rc.get("root_cause_code", "N/A")
                title = rc.get("root_cause_title", "N/A")[:50]
                print_info(f"[{i}] {code} - {title}")
            
            # Save JSON
            scenario_slug = self.name.lower().replace(" ", "_")
            json_file = f"outputs/{scenario_slug}_{self.timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(part3, f, ensure_ascii=False, indent=2)
            print_success(f"JSON: {json_file}")
            self.results["files"].append(json_file)
            
            self.results["steps"]["rca"] = "PASSED"
            self.results["part3"] = part3
            
            return part3
            
        except Exception as e:
            print_error(f"Hata: {e}")
            self.results["steps"]["rca"] = "FAILED"
            raise
    
    def _run_docx_generation(self, part1: Dict, part2: Dict, part3: Dict):
        """Run SkillBasedDocxAgent."""
        print_section("ADIM 5: SkillBasedDocxAgent")
        
        try:
            agent = SkillBasedDocxAgent()
            print_success("Agent başlatıldı")
            
            combined_data = {
                "part1": part1,
                "part2": part2,
                "part3_rca": part3
            }
            
            ref_no = part1.get("ref_no", "UNKNOWN")
            scenario_slug = self.name.lower().replace(" ", "_")
            
            output_path = f"outputs/INC-{ref_no}_{scenario_slug}.docx"
            docx_file = agent.generate_report(
                combined_data,
                output_path=output_path
            )
            
            # HTML dosyası docx_file ile aynı isimde ama .html uzantılı
            html_file = docx_file.replace(".docx", ".html") if docx_file else None
            
            if docx_file and Path(docx_file).exists():
                size = Path(docx_file).stat().st_size / 1024
                print_success(f"DOCX: {docx_file} ({size:.1f} KB)")
                self.results["files"].append(docx_file)
            
            if html_file and Path(html_file).exists():
                size = Path(html_file).stat().st_size / 1024
                print_success(f"HTML: {html_file} ({size:.1f} KB)")
                self.results["files"].append(html_file)
            
            self.results["steps"]["docx"] = "PASSED"
            
        except Exception as e:
            print_error(f"Hata: {e}")
            self.results["steps"]["docx"] = "FAILED"
            raise


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests(scenarios: Optional[List[str]] = None) -> Dict:
    """Run all test scenarios."""
    
    # Define all scenarios
    all_scenarios = {
        "fall": ("Yüksekten Düşme", INCIDENT_FALL_FROM_HEIGHT),
        "electrical": ("Elektrik Çarpması", INCIDENT_ELECTRICAL_SHOCK),
        "machine": ("Makine Sıkışması", INCIDENT_MACHINE_ENTRAPMENT)
    }
    
    # Filter scenarios if specified
    if scenarios:
        test_scenarios = {k: v for k, v in all_scenarios.items() if k in scenarios}
    else:
        test_scenarios = all_scenarios
    
    print_banner("HSE KÖK NEDEN ANALİZİ\nKAPSAMLI TEST PAKETİ", "=")
    print_info(f"Test Sayısı: {len(test_scenarios)}")
    print_info(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    start_time = time.time()
    
    # Run each scenario
    for key, (name, data) in test_scenarios.items():
        test = ScenarioTest(name, data)
        result = test.run()
        results.append(result)
        
        # Small delay between tests to help cache
        if len(test_scenarios) > 1:
            time.sleep(2)
    
    # Overall summary
    total_duration = time.time() - start_time
    
    print_banner("GENEL ÖZET", "=")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    
    print(f"  Toplam Test: {total_tests}")
    print(f"  Başarılı: {passed_tests}")
    print(f"  Başarısız: {total_tests - passed_tests}")
    print(f"  Toplam Süre: {total_duration:.1f} saniye")
    print(f"  Ortalama Süre: {total_duration/total_tests:.1f} saniye/test")
    
    print("\n  Test Detayları:")
    for r in results:
        scenario = r["results"]["scenario"]
        status = "✅ PASSED" if r["success"] else "❌ FAILED"
        duration = r["results"].get("duration", 0)
        print(f"    {status} - {scenario} ({duration:.1f}s)")
    
    # All files generated
    all_files = []
    for r in results:
        all_files.extend(r["results"].get("files", []))
    
    if all_files:
        print(f"\n  Toplam {len(all_files)} dosya oluşturuldu:")
        for f in all_files:
            print(f"    📄 {f}")
    
    # Cache info
    print("\n  💎 Prompt Caching:")
    print("    İlk test: Cache write")
    print("    Sonraki testler: Cache hit (%90 tasarruf)")
    print("    OpenRouter: https://openrouter.ai/activity")
    
    return {
        "total": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "duration": total_duration,
        "results": results
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HSE Kök Neden Analizi - Kapsamlı Test Paketi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python test_all_scenarios.py              # Tüm senaryolar
  python test_all_scenarios.py --fall       # Sadece düşme
  python test_all_scenarios.py --electrical # Sadece elektrik
  python test_all_scenarios.py --machine    # Sadece makine
  python test_all_scenarios.py --fall --electrical  # Düşme + elektrik
        """
    )
    
    parser.add_argument(
        "--fall",
        action="store_true",
        help="Yüksekten düşme senaryosunu çalıştır"
    )
    
    parser.add_argument(
        "--electrical",
        action="store_true",
        help="Elektrik çarpması senaryosunu çalıştır"
    )
    
    parser.add_argument(
        "--machine",
        action="store_true",
        help="Makine sıkışması senaryosunu çalıştır"
    )
    
    args = parser.parse_args()
    
    # Determine which scenarios to run
    scenarios = []
    if args.fall:
        scenarios.append("fall")
    if args.electrical:
        scenarios.append("electrical")
    if args.machine:
        scenarios.append("machine")
    
    # If no specific scenario selected, run all
    if not scenarios:
        scenarios = None
    
    # Run tests
    try:
        summary = run_all_tests(scenarios)
        
        # Exit code based on results
        if summary["failed"] == 0:
            print("\n🎉 TÜM TESTLER BAŞARILI!")
            sys.exit(0)
        else:
            print(f"\n⚠️  {summary['failed']} TEST BAŞARISIZ!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test kullanıcı tarafından durduruldu")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
