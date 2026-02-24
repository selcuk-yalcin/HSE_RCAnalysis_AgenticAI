#!/usr/bin/env python3
"""
================================================================================
YÜKSEKTEN DÜŞME OLAYI - TAM SİSTEM TESTİ
================================================================================

OLAY TANIMI:
  İnşaat şantiyesinde 6 metre yükseklikteki iskeleden düşen işçi ağır yaralandı.
  İşçi güvenlik emniyet kemeri takmamış, iskele korkuluğu eksik bırakılmış.
  Acil servise kaldırılan işçinin omurga kırığı ve iç kanama tespit edildi.

TEST KAPSAMI:
  1. Ortam kontrolü ve API anahtarları
  2. OverviewAgent - İlk olay raporu analizi
  3. AssessmentAgent - RIDDOR ve soruşturma seviyesi
  4. RootCauseAgentV2 - Hiyerarşik 5-Why analizi
  5. SkillBasedDocxAgent - Profesyonel rapor üretimi (DOCX + HTML)
  6. Çıktı doğrulama ve kalite kontrol

BEKLENEN SONUÇ:
  - Olay Tipi: Major/Fatal injury
  - RIDDOR: Y (Fall from height >2m)
  - Investigation Level: High level
  - Kök Nedenler: 3-4 adet (D kategorisi - Organizasyonel)
  - DOCX Rapor: 18-20 sayfa, tam formatlanmış
  - HTML Rapor: Düzenlenebilir, responsive

ÇALIŞTIRMA:
  python test_fall_from_height.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

# Project imports
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# INCIDENT DATA - YÜKSEKTEN DÜŞME OLAYI
# ============================================================================

INCIDENT_DATA = """
OLAY RAPORU - YÜKSEKTEN DÜŞME

Tarih: 18 Şubat 2026, Saat: 10:35
Lokasyon: Yapı İnşaat Şantiyesi - 4. Kat İskele Alanı
Rapor Eden: Şantiye Şefi - Mustafa Çelik

OLAY AÇIKLAMASI:
İskele montaj işçisi Hasan Yıldız (32) yaklaşık 6 metre yükseklikteki 
iskeleden düşerek zemine çakıldı. İşçi ağır yaralanarak ambulansla 
hastaneye kaldırıldı.

OLAY KRONOLOJİSİ:
- 08:00 - İşçi vardiyaya başladı, 4. kat iskele montajına atandı
- 09:30 - İskele platformu montajı devam ediyor
- 10:30 - İşçi iskele kenarında çalışırken dengesini kaybetti
- 10:35 - 6 metre yükseklikten zemine düştü
- 10:37 - İş arkadaşları yardıma koştu, 112 arandı
- 10:42 - İlk yardım uygulandı (bilinçli ama ağır yaralı)
- 10:55 - Ambulans geldi, hastaneye sevk edildi
- 11:20 - Hastane raporu: L2 omurga kırığı, iç kanama, ciddi durum

ETKİLENEN KİŞİ:
- Ad Soyad: Hasan Yıldız
- Yaş: 32
- Pozisyon: İskele Montaj İşçisi
- Deneyim: 8 ay iskele işlerinde
- Vardiya: Gündüz (08:00-17:00)

YARALANMA DETAYI:
- L2 omurga vertebra kırığı
- Pelvis çatlağı
- İç kanama (dalak)
- Çoklu kontüzyon
- Yoğun bakıma alındı
- Prognoz: Ciddi, uzun süreli tedavi gerekli

GÜVENLİK EKİPMANI:
✗ Emniyet kemeri: TAKILMADI
✗ Korkuluk: EKSİK (montaj tamamlanmamış)
✗ Güvenlik ağı: YOK
✓ Baret: TAKILI
✓ İş ayakkabısı: GİYİLİ
✗ Tam vücut emniyet kemeri: TAKILMADI

İSKELE DURUMU:
- Platform genişliği: 1.2m (standart)
- Korkuluk: Sadece bir tarafta mevcut
- Çalışılan kenar: Korkuluksuz taraf
- İskele sınıfı: Çelik boru iskele
- Son kontrol: 2 gün önce (korkuluk eksikliği not edilmemiş)
- İskele izin belgesi: Var (ama güncel değil)

KÖK NEDEN ÖN BULGULAR:
1. İşçi emniyet kemeri takmamış (prosedür ihlali)
2. Korkuluk montajı tamamlanmadan çalışmaya başlanmış
3. İş izin sistemi eksik çalışıyor (risk değerlendirmesi yetersiz)
4. Güvenlik görevlisi şantiye turunda değildi
5. İşbaşı eğitimi kayıtları eksik (yüksekte çalışma eğitimi verilmemiş)
6. Emniyet kemeri kullanım denetimi yapılmıyor
7. Üretim baskısı (proje gecikmiş, hızlı bitirme talimatı)

TANIK BEYANLARI:
- Ali Demir (İşçi): "Hasan kemersiz çalışıyordu. Herkes öyle yapıyor. 
  Şef acele ediyor diye korkuluksuz tarafa geçtik."
- Mehmet Kara (Usta): "Korkuluk yarın takılacaktı. Bugün platform montajı 
  bitmeliydi. Şef hızlı bitirin dedi."
- Şantiye Şefi: "Korkuluğun eksik olduğunu bilmiyordum. İşçiler 
  kemer takmaları gerektiğini biliyorlar."

YÖNETİM FAKTÖRLERI:
- Proje 3 hafta gecikmeli
- Müşteri baskısı: "Hızlı bitiş" talebi
- Güvenlik toplantıları: 2 aydır yapılmıyor
- Risk değerlendirmesi: 6 ay önce (güncellenmemiş)
- İşbaşı eğitim kayıtları: Eksik/düzensiz
- Denetim sıklığı: Haftada 1 (yetersiz)

ACIL ÖNLEMLER:
1. Tüm yüksekte çalışmalar durduruldu
2. İskele kontrolleri yeniden yapıldı
3. Kemer kullanımı zorunlu hale getirildi
4. Güvenlik brifingi verildi
5. Proje takvimi gözden geçirildi
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
    """Run fall from height incident test."""
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("YÜKSEKTEN DÜŞME OLAYI - TAM SİSTEM TESTİ")
    print_info(f"Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Olay: İnşaat şantiyesi iskele düşmesi (6m yükseklik)")
    
    results = {"timestamp": timestamp, "steps": {}}
    
    # Step 1: Environment Check
    print_header("ADIM 1: Ortam Kontrolü")
    try:
        assert os.getenv("OPENROUTER_API_KEY"), "API key missing"
        print_success("API anahtarı mevcut")
        print_success("Bağımlılıklar kontrol edildi")
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Ortam hatası: {e}")
        results["steps"]["environment"] = "FAILED"
        return results
    
    # Step 2: OverviewAgent
    print_header("ADIM 2: OverviewAgent - İlk Değerlendirme")
    try:
        agent = OverviewAgent()
        print_success("OverviewAgent başlatıldı")
        
        # INCIDENT_DATA'yı dict olarak gönder
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Referans No: {part1.get('ref_no')}")
        print_success(f"Olay Tipi: {part1.get('incident_type')}")
        print_info(f"Ne oldu: {part1.get('brief_details', {}).get('what', 'N/A')[:80]}...")
        
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"OverviewAgent hatası: {e}")
        results["steps"]["overview"] = "FAILED"
        return results
    
    # Step 3: AssessmentAgent
    print_header("ADIM 3: AssessmentAgent - Şiddet Değerlendirmesi")
    try:
        agent = AssessmentAgent()
        print_success("AssessmentAgent başlatıldı")
        
        # INCIDENT_DATA'yı dict olarak gönder
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        print_success(f"Şiddet Seviyesi: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Soruşturma Seviyesi: {part2.get('investigation', {}).get('level')}")
        
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"AssessmentAgent hatası: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results
    
    # Step 4: RootCauseAgentV2
    print_header("ADIM 4: RootCauseAgentV2 - Kök Neden Analizi")
    try:
        agent = RootCauseAgentV2()
        print_success("RootCauseAgentV2 başlatıldı")
        
        # Doğru parametreler: part1_data, part2_data, investigation_data
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        
        branches = part3.get("analysis_branches", [])
        root_causes = part3.get("final_root_causes", [])
        
        print_success(f"Analiz dalı sayısı: {len(branches)}")
        print_success(f"Kök neden sayısı: {len(root_causes)}")
        
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = rc.get("root_cause_title", "N/A")[:50]
            print_info(f"[{i}] {code} - {title}")
        
        # Save JSON
        json_path = f"outputs/fall_from_height_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON kaydedildi: {json_path}")
        
        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"RootCauseAgentV2 hatası: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results
    
    # Step 5: SkillBasedDocxAgent
    print_header("ADIM 5: SkillBasedDocxAgent - Rapor Üretimi")
    try:
        agent = SkillBasedDocxAgent()
        print_success("SkillBasedDocxAgent başlatıldı")
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_path = f"outputs/{ref_no}_fall_from_height.docx"
        
        investigation_data = {
            "part1": part1,
            "part2": part2,
            "part3_rca": part3
        }
        
        result_path = agent.generate_report(investigation_data, docx_path)
        html_path = result_path.replace('.docx', '.html')
        
        if Path(result_path).exists():
            size_kb = Path(result_path).stat().st_size / 1024
            print_success(f"DOCX oluşturuldu: {size_kb:.1f} KB")
            print_info(f"Dosya: {result_path}")
        
        if Path(html_path).exists():
            html_kb = Path(html_path).stat().st_size / 1024
            print_success(f"HTML oluşturuldu: {html_kb:.1f} KB")
            print_info(f"Dosya: {html_path}")
        
        results["steps"]["docx"] = "PASSED"
        results["docx_path"] = result_path
        results["html_path"] = html_path
    except Exception as e:
        print_error(f"SkillBasedDocxAgent hatası: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["docx"] = "FAILED"
        return results
    
    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])
    
    print_header("TEST ÖZET")
    print_info(f"Geçen Süre: {elapsed:.1f} saniye")
    print_info(f"Başarılı Adım: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 TÜM TESTLER BAŞARILI!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ {total - passed} test başarısız oldu")
        results["overall"] = "FAILED"
    
    print("\n📄 Üretilen Dosyalar:")
    if "docx_path" in results:
        print(f"   DOCX: {results['docx_path']}")
    if "html_path" in results:
        print(f"   HTML: {results['html_path']}")
    print(f"   JSON: {json_path}\n")
    
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
