#!/usr/bin/env python3
"""
================================================================================
ELEKTRİK ÇARPMASI OLAYI - TAM SİSTEM TESTİ
================================================================================
!!!! teste aydinlatma ile ilgili birseyler ekle ve bunu bot kisminda da kullanacagim
OLAY TANIMI:
  Bakım teknisyeni elektrik panosunda çalışırken 380V yüksek voltaj akımına
  kapıldı. Elektrik sistemi enerjili haldeyken çalışıldı, kilitlama prosedürü
  (LOTO - Lockout/Tagout) uygulanmamış. Teknisyen hastaneye kaldırıldı.

TEST KAPSAMI:
  1. Ortam ve API kontrolleri
  2. OverviewAgent - Elektrik olayı ilk değerlendirme
  3. AssessmentAgent - Şiddet ve RIDDOR sınıflandırması
  4. RootCauseAgentV2 - LOTO eksikliği kök neden analizi
  5. SkillBasedDocxAgent - Kapsamlı rapor (DOCX + HTML)
  6. Çıktı kalite kontrolü

BEKLENEN SONUÇ:
  - Olay Tipi: Electrical injury
  - RIDDOR: Y (Electrical shock injury)
  - Investigation Level: High level
  - Kök Nedenler: LOTO prosedürü eksikliği, eğitim yetersizliği
  - Dallar: 3-4 (Prosedürel, eğitim, denetim)

ÇALIŞTIRMA:
  python test_electrical_shock.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
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

ELEKTRİK PANOSUdeğil DURUMU:
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


def print_info(msg: str):
    print(f"     {msg}")


def main():
    """Run electrical shock incident test."""
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("ELEKTRİK ÇARPMASI OLAYI - TAM SİSTEM TESTİ")
    print_info(f"Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Olay: 380V elektrik panosunda LOTO prosedürü uygulanmadan çalışma")
    
    results = {"timestamp": timestamp, "steps": {}, "files": []}
    
    # Environment check
    print_header("ADIM 1: Ortam Kontrolü")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        assert api_key, "OPENROUTER_API_KEY bulunamadı"
        print_success(f"API Key: {api_key[:12]}...{api_key[-4:]}")
        
        Path("outputs").mkdir(exist_ok=True)
        print_success("Çıktı dizini hazır")
        
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
        
        # INCIDENT_DATA string'i dict formatına çevir
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Ref No: {part1.get('ref_no')}")
        print_success(f"Olay Tipi: {part1.get('incident_type')}")
        
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Hata: {e}")
        results["steps"]["overview"] = "FAILED"
        return results
    
    # AssessmentAgent
    print_header("ADIM 3: AssessmentAgent")
    try:
        agent = AssessmentAgent()
        # INCIDENT_DATA'yı dict olarak gönder
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        
        print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Level: {part2.get('investigation', {}).get('level')}")
        
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Hata: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results
    
    # RootCauseAgentV2
    print_header("ADIM 4: RootCauseAgentV2")
    try:
        agent = RootCauseAgentV2()
        # Doğru parametreler: part1_data, part2_data, investigation_data
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        
        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])
        
        print_success(f"Dallar: {len(branches)}")
        print_success(f"Kök nedenler: {len(causes)}")
        
        for i, rc in enumerate(causes, 1):
            print_info(f"[{i}] {rc.get('root_cause_code')} - {rc.get('root_cause_title', '')[:40]}")
        
        json_file = f"outputs/electrical_shock_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON: {json_file}")
        results["files"].append(json_file)
        
        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results
    
    # SkillBasedDocxAgent
    print_header("ADIM 5: Rapor Üretimi (DOCX + HTML)")
    try:
        agent = SkillBasedDocxAgent()
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = f"outputs/{ref_no}_electrical_shock.docx"
        
        data = {"part1": part1, "part2": part2, "part3_rca": part3}
        result = agent.generate_report(data, docx_file)
        
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
        return results
    
    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])
    
    print_header("TEST ÖZET")
    print_info(f"Süre: {elapsed:.1f} saniye")
    print_info(f"Sonuç: {passed}/{total} adım başarılı")
    
    if passed == total:
        print_success("🎉 TÜM TESTLER BAŞARILI!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ {total-passed} test başarısız")
        results["overall"] = "FAILED"
    
    print("\n📄 Üretilen Dosyalar:")
    for f in results["files"]:
        print(f"   • {f}")
    print()
    
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
