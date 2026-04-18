#!/usr/bin/env python3
"""
================================================================================
ELEKTRİK ÇARPMASI OLAYI - DSPy V3.1 TAM SİSTEM TESTİ
================================================================================

OLAY TANIMI:
  Bakım teknisyeni elektrik panosunda çalışırken 380V yüksek voltaj akımına
  kapıldı. Elektrik sistemi enerjili haldeyken çalışıldı, kilitleme prosedürü
  (LOTO - Lockout/Tagout) uygulanmamış. Teknisyen hastaneye kaldırıldı.

TEST KAPSAMI:
  1. Ortam ve API kontrolleri
  2. OverviewAgent - Elektrik olayı ilk değerlendirme
  3. AssessmentAgent - Şiddet ve RIDDOR sınıflandırması
  4. ✨ RootCauseAgentV3_1 (DSPy) - LOTO eksikliği kök neden analizi
  5. SkillBasedDocxAgent - Kapsamlı rapor (DOCX + HTML)
  6. Çıktı kalite kontrolü

FARK (V2'den):
  ✨ DSPy-powered 5-Why analizi
  ✨ Daha yapılandırılmış root cause çıkarımı
  ✨ Meta-synthesis ile nihai kök neden belirleme

BEKLENEN SONUÇ:
  - Olay Tipi: Electrical injury
  - RIDDOR: Y (Electrical shock injury)
  - Investigation Level: High level
  - Kök Nedenler: LOTO prosedürü eksikliği, eğitim yetersizliği
  - Dallar: 3-4 (Prosedürel, eğitim, denetim)

ÇALIŞTIRMA:
  conda activate hse_dspy
  python tests/test_electrical_shock_dspy.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# ============================================
# PATH SETUP (Proje root'u Python path'e ekle)
# ============================================
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import agents
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# INCIDENT DATA - ELEKTRİK ÇARPMASI
# ============================================================================

INCIDENT_DATA = """
OLAY RAPORU - ELEKTRİK ÇARPMASI

Tarih: 20 Şubat 2026, Saat: 15:20
Lokasyon: Üretim Tesisi - Ana Elektrik Panosu (MDB-02)
Rapor Eden: Elektrik Bakım Sorumlusu - İbrahim Aydın

OLAY AÇIKLAMASI:
Bakım teknisyeni Kemal Arslan (29) elektrik panosunda arıza giderme 
çalışması yaparken 380V yüksek voltaj akımına kapıldı. Teknisyen 
elektrik çarpması sonucu yere düştü ve bilinçsiz hale geldi.

OLAY KRONOLOJİSİ:
- 14:30 - Üretim hattında elektrik arızası bildirildi
- 14:45 - Kemal Arslan panoya baktı, ana şalter arızası tespit etti
- 15:00 - Arıza gidermek için panoya müdahale kararı alındı
- 15:10 - Kemal pano kapağını açtı (elektrik enerjili halde)
- 15:20 - Şalter bağlantısına dokunurken elektrik çarptı
- 15:21 - İş arkadaşları yardıma koştu, ana şalter kapatıldı
- 15:22 - İlk yardım uygulandı, kalp masajı başlatıldı
- 15:25 - 112 arandı, ambulans çağrıldı
- 15:35 - Ambulans geldi, defibrilasyon uygulandı
- 15:50 - Hastaneye sevk, yoğun bakıma alındı

ETKİLENEN KİŞİ:
- Ad Soyad: Kemal Arslan
- Yaş: 29
- Pozisyon: Elektrik Bakım Teknisyeni
- Deneyim: 4 yıl (elektrik bakım)
- Sertifikalar: Elektrik İşlerinde Yetkili Kişi Belgesi (var)
- Son eğitim: 10 ay önce (Temel Elektrik Güvenliği)

YARALANMA:
- Elektrik çarpması (380V, 3-faz)
- Kardiyak arrest (30 saniye)
- 2. derece yanık (sağ el ve kol)
- Kas hasarı (elektrik akımı geçişi)
- Yoğun bakım: 2 gün
- Taburcu: 1 hafta sonra (tam iyileşme 3 ay)

GÜVENLİK PROSEDÜRÜ İHLALLERİ:
✗ LOTO (Lockout/Tagout) prosedürü uygulanmadı
✗ Elektrik enerjisi kesilmedi
✗ Test cihazı (voltmetre) kullanılmadı
✗ Yalıtımlı eldiven giyilmedi
✗ Yalıtkan ayakkabı giyilmedi
✗ İş izin belgesi alınmadı
✗ İkinci kişi (gözetleyici) bulunmuyordu
✓ Baret takılıydı (ancak yetersiz)

ELEKTRİK PANOSUNUN DURUMU:
- Pano tipi: 380V, 3-faz, 630A ana şalter
- Uyarı levhaları: Mevcut ("Yüksek Voltaj - Tehlike")
- Kilit sistemi: Var (ancak kilitlenmemiş)
- Son bakım: 3 ay önce
- Termografi testi: 6 ay önce (anormallik tespit edilmemiş)
- Arıza geçmişi: 2 kez benzer şalter sorunu

LOTO (LOCKOUT/TAGOUT) PROSEDÜRÜ:
❌ UYGULANMADI
- Prosedür dokümanı: VAR (ancak uygulanmıyor)
- LOTO kitleri: Depoda mevcut (kullanılmıyor)
- LOTO eğitimi: 2 yıl önce verilmiş (tekrar yok)
- Uygulama denetimi: Yapılmıyor
- Son LOTO denetimi: Hiç yapılmamış

KÖK NEDEN ÖN BULGULAR:
1. LOTO prosedürü kâğıt üzerinde var, pratikte uygulanmıyor
2. "Üretim durmasın" baskısı - enerji kesme korkusu
3. Risk normalleşmesi: "Hızlıca hallederiz" anlayışı
4. Gözetim eksikliği: Elektrik işlerinde ikinci kişi zorunluluğu yok
5. Eğitim yetersiz: Son LOTO eğitimi 2 yıl önce
6. Denetim eksikliği: Bakım işleri düzenli denetlenmiyor
7. İş izin sistemi: Elektrik işleri için zorunlu değil

TANIK BEYANLARI:
- Ali Yılmaz (Teknisyen): "Kemal acele ediyordu. Üretim duracak diye 
  enerjiyi kesmedi. Hep böyle yapıyoruz aslında."
- Üretim Müdürü: "Elektrik kesilirse 2 saat üretim kaybı olur. 
  Teknisyenler dikkatli çalışırlarsa sorun olmaz."
- Bakım Sorumlusu: "LOTO prosedürü var ama üretim aksamasın diye 
  pek uygulamıyoruz. Tecrübeli teknisyenler dikkat eder."

YÖNETİM FAKTÖRLERI:
- Üretim hedefi baskısı: Duruş süreleri minimize edilmeli
- LOTO kültürü yok: "Gereksiz zaman kaybı" görüşü
- Güvenlik vs üretim dengesi: Üretim öncelikli
- Performans ölçümü: Duruş süreleri takip ediliyor (güvenlik değil)
- Prosedür uyumu denetimi: Yapılmıyor

ACIL ÖNLEMLER:
1. Tüm elektrik işleri durduruldu
2. LOTO prosedürü zorunlu hale getirildi
3. Elektrik işleri için iş izin sistemi başlatıldı
4. Tüm teknisyenlere LOTO eğitimi verildi
5. LOTO kitleri tüm teknisyenlere dağıtıldı
6. Elektrik işlerinde ikinci kişi zorunluluğu getirildi
"""


# ============================================================================
# TEST EXECUTION
# ============================================================================

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_warning(msg: str):
    print(f"  ⚠️  {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def print_dspy_info(msg: str):
    print(f"  ✨ {msg}")


def main():
    """Run electrical shock incident test with DSPy V3.1."""
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("ELEKTRİK ÇARPMASI OLAYI - DSPy V3.1 TAM SİSTEM TESTİ")
    print_info(f"Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Olay: 380V elektrik panosunda LOTO prosedürü uygulanmadan çalışma")
    print_dspy_info("DSPy-powered root cause analysis aktif")
    
    results = {"timestamp": timestamp, "steps": {}, "files": [], "dspy_enabled": False}
    
    # Environment check
    print_header("ADIM 1: Ortam Kontrolü")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        assert api_key, "OPENROUTER_API_KEY bulunamadı"
        print_success(f"API Key: {api_key[:12]}...{api_key[-4:]}")
        
        # DSPy check
        try:
            import dspy
            print_dspy_info(f"DSPy kurulu: v{dspy.__version__}")
            results["dspy_enabled"] = True
        except ImportError:
            print_warning("DSPy bulunamadı, V2 fallback kullanılacak")
            results["dspy_enabled"] = False
        
        output_dir = Path("outputs/electrical_shock_dspy")
        output_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Çıktı dizini: {output_dir}")
        
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Ortam hatası: {e}")
        results["steps"]["environment"] = "FAILED"
        return results
    
    # OverviewAgent
    print_header("ADIM 2: OverviewAgent")
    try:
        agent = OverviewAgent()
        print_success("Agent başlatıldı")
        
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Ref No: {part1.get('ref_no')}")
        print_success(f"Olay Tipi: {part1.get('incident_type')}")
        print_info(f"Lokasyon: {part1.get('location', {}).get('facility', 'N/A')}")
        
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["overview"] = "FAILED"
        return results
    
    # AssessmentAgent
    print_header("ADIM 3: AssessmentAgent")
    try:
        agent = AssessmentAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        
        print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Level: {part2.get('investigation', {}).get('level')}")
        
        # RIDDOR detay
        riddor = part2.get('riddor', {})
        if riddor.get('reportable') == 'Y':
            print_info(f"RIDDOR Kategori: {riddor.get('category', 'N/A')}")
        
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["assessment"] = "FAILED"
        return results
    
    # RootCauseAgentV3_1 (DSPy)
    print_header("ADIM 4: RootCauseAgentV3_1 (✨ DSPy Powered)")
    try:
        print_dspy_info("DSPy-based 5-Why analysis başlatılıyor...")
        
        agent = RootCauseAgentV3_1(
            use_rag=False,  # RAG disabled (dependency issues)
            enable_diversity_check=True
        )
        print_success("V3.1 agent başlatıldı (DSPy + diversity check)")
        
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        
        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])
        
        print_dspy_info(f"Analiz dalları: {len(branches)}")
        print_dspy_info(f"Kök nedenler: {len(causes)}")
        
        # Branch detayları
        for i, branch in enumerate(branches, 1):
            branch_name = branch.get("branch_name", f"Branch {i}")
            why_count = len(branch.get("five_why_analysis", []))
            print_info(f"[Dal {i}] {branch_name} - {why_count} Why")
        
        # Kök neden özetleri
        print_info("Kök Nedenler:")
        for i, rc in enumerate(causes, 1):
            code = rc.get('root_cause_code', 'N/A')
            title = rc.get('root_cause_title', 'N/A')[:60]
            print_info(f"  [{i}] {code} - {title}")
        
        # JSON kaydet
        json_file = output_dir / f"electrical_shock_dspy_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON: {json_file}")
        results["files"].append(str(json_file))
        
        results["steps"]["rca_dspy"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca_dspy"] = "FAILED"
        return results
    
    # SkillBasedDocxAgent
    print_header("ADIM 5: Rapor Üretimi (DOCX + HTML)")
    try:
        agent = SkillBasedDocxAgent()
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = output_dir / f"{ref_no}_electrical_shock_dspy.docx"
        
        data = {"part1": part1, "part2": part2, "part3_rca": part3}
        result = agent.generate_report(data, str(docx_file))
        
        html_file = result.replace('.docx', '.html')
        
        if Path(result).exists():
            size = Path(result).stat().st_size / 1024
            print_success(f"DOCX: {size:.1f} KB - {result}")
            results["files"].append(result)
        
        if Path(html_file).exists():
            html_size = Path(html_file).stat().st_size / 1024
            print_success(f"HTML: {html_size:.1f} KB - {html_file}")
            results["files"].append(html_file)
        
        results["steps"]["report"] = "PASSED"
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["report"] = "FAILED"
        # Don't return, continue to summary
    
    # Quality checks
    print_header("ADIM 6: Kalite Kontrolleri")
    quality_checks = []
    
    # Check 1: Incident type
    if part1.get("incident_type") == "Electrical injury":
        print_success("Olay tipi doğru (Electrical injury)")
        quality_checks.append("incident_type")
    else:
        print_warning(f"Olay tipi beklenen değil: {part1.get('incident_type')}")
    
    # Check 2: RIDDOR
    if part2.get("riddor", {}).get("reportable") == "Y":
        print_success("RIDDOR doğru (Y - Reportable)")
        quality_checks.append("riddor")
    else:
        print_warning("RIDDOR beklenmeyen değer")
    
    # Check 3: Investigation level
    inv_level = part2.get("investigation", {}).get("level", "").lower()
    if "high" in inv_level:
        print_success("Investigation level doğru (High level)")
        quality_checks.append("investigation_level")
    else:
        print_warning(f"Investigation level: {inv_level}")
    
    # Check 4: Root causes count
    if len(causes) >= 2:
        print_success(f"Yeterli kök neden ({len(causes)} adet)")
        quality_checks.append("root_causes_count")
    else:
        print_warning(f"Az kök neden: {len(causes)}")
    
    # Check 5: LOTO mention
    part3_str = json.dumps(part3, ensure_ascii=False).lower()
    if "loto" in part3_str or "lockout" in part3_str or "tagout" in part3_str:
        print_success("LOTO prosedürü analiz edilmiş")
        quality_checks.append("loto_mentioned")
    else:
        print_warning("LOTO prosedürü eksik")
    
    results["quality_checks"] = len(quality_checks)
    results["steps"]["quality"] = "PASSED" if len(quality_checks) >= 4 else "PARTIAL"
    
    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])
    
    print_header("TEST ÖZET")
    print_info(f"Süre: {elapsed:.1f} saniye")
    print_info(f"Sonuç: {passed}/{total} adım başarılı")
    print_info(f"Kalite: {len(quality_checks)}/5 kontrol geçti")
    
    if results["dspy_enabled"]:
        print_dspy_info("DSPy V3.1 başarıyla kullanıldı")
    
    if passed == total:
        print_success("🎉 TÜM TESTLER BAŞARILI!")
        results["overall"] = "PASSED"
    elif passed >= total - 1:
        print_warning(f"⚠️  {total-passed} test kısmi başarı")
        results["overall"] = "PARTIAL"
    else:
        print_error(f"❌ {total-passed} test başarısız")
        results["overall"] = "FAILED"
    
    print("\n📄 Üretilen Dosyalar:")
    for f in results["files"]:
        print(f"   • {f}")
    
    # Final summary file
    summary_file = output_dir / f"test_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "elapsed_seconds": elapsed,
            "dspy_enabled": results["dspy_enabled"],
            "steps": results["steps"],
            "quality_checks": results.get("quality_checks", 0),
            "overall": results["overall"],
            "files": results["files"]
        }, f, ensure_ascii=False, indent=2)
    print(f"\n📊 Test özeti: {summary_file}\n")
    
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") in ["PASSED", "PARTIAL"] else 1)
