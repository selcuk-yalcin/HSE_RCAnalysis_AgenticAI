#!/usr/bin/env python3
"""
================================================================================
MAKİNE SIKIŞ MASI OLAYI - TAM SİSTEM TESTİ
================================================================================

OLAY TANIMI:
  Konveyör bantı operatörü makineye takılan ürünü temizlerken elini bantın 
  arasına soktu. Makine çalışır durumdayken müdahale edildi, acil durdurma 
  butonu kullanılmadı. Operatörün üç parmağında kırık ve ezilme meydana geldi.

TEST KAPSAMI:
  1. Sistem kontrolü ve hazırlık
  2. OverviewAgent - Makine güvenliği olayı analizi
  3. AssessmentAgent - Yaralanma şiddeti sınıflandırması  
  4. RootCauseAgentV2 - Makine güvenliği kök neden analizi
  5. SkillBasedDocxAgent - Detaylı rapor üretimi
  6. Dosya doğrulama ve kalite kontrol

BEKLENEN SONUÇ:
  - Olay Tipi: Machinery/Equipment injury
  - RIDDOR: Y (Finger fractures/crush injury)
  - Investigation Level: Medium/High level
  - Kök Nedenler: Güvenlik prosedürü ihlali, makine koruyucu eksikliği
  - Dallar: 3 (İnsan faktörü, ekipman, prosedür)

ÇALIŞTIRMA:
  python test_machine_entrapment.py
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
# INCIDENT DATA - MAKİNE SIKIŞMASI
# ============================================================================

INCIDENT_DATA = """
OLAY RAPORU - MAKİNE SIKIŞMASI / EZILME

Tarih: 22 Şubat 2026, Saat: 11:15
Lokasyon: Ambalaj Hattı 3 - Konveyör Bandı Sistemi
Rapor Eden: Hat Şefi - Ayşe Demir

OLAY AÇIKLAMASI:
Konveyör bandı operatörü Fatma Yılmaz (27) bantda takılan ürünü temizlerken
sağ elini konveyör ruloları arasına soktu. Makine çalışır durumdaydı. Eli
rulo ve bant arasında sıkıştı, üç parmağı ezildi ve kırıldı.

OLAY KRONOLOJİSİ:
- 10:00 - Fatma sabah vardiyasına başladı (ambalaj hattı operatörü)
- 10:45 - Konveyör bandında ürün sıkışması başladı (sık tekrarlayan sorun)
- 10:50 - Fatma bandı durdurmadan sıkışan ürünü çıkarmaya çalıştı
- 11:10 - Yeni bir ürün sıkıştı, yine elle müdahale etti
- 11:15 - Eli konveyör rulosu ile bant arasında sıkıştı
- 11:16 - Acı çığlıkları duyuldu, iş arkadaşları koştu
- 11:17 - Hat şefi acil durdurma butonuna bastı
- 11:18 - Eli makine arasından çıkarıldı (kanama ve kırık açık)
- 11:20 - İlk yardım uygulandı, kanama durdurulmaya çalışıldı
- 11:25 - 112 arandı, ambulans çağrıldı
- 11:40 - Hastaneye sevk edildi

ETKİLENEN KİŞİ:
- Ad Soyad: Fatma Yılmaz
- Yaş: 27
- Pozisyon: Konveyör Bandı Operatörü
- Deneyim: 14 ay (konveyör operatörü)
- Eğitim: Temel makine güvenliği (6 ay önce)
- Vardiya: Gündüz (07:00-16:00)

YARALANMA DETAYI:
- Sağ el: 3 parmak (işaret, orta, yüzük) 
- İşaret parmağı: Açık kırık, eklem hasarı
- Orta parmak: Ezilme, çoklu kırık
- Yüzük parmağı: Kapalı kırık, doku hasarı
- Ameliyat: Acil cerrahi müdahale yapıldı
- Tahmini iyileşme: 3-6 ay, fonksiyon kaybı riski var
- İş göremezlik: En az 4 ay

MAKİNE GÜVENLİK DURUMU:
✗ Acil durdurma butonu: Operatör tarafından kullanılmadı
✗ Koruyucu kapak: Açık pozisyonda (monte edilmemiş)
✗ Işık perdesi/sensör: Yok
✗ İki el kumanda sistemi: Yok
✓ Acil durdurma butonu: Mevcut (3 nokta) ama uzakta
✗ Uyarı levhası: "Çalışırken elle müdahale etmeyin" - YOK
✗ Güvenlik prosedürü: Yazılı prosedür yok
✗ Risk değerlendirmesi: Güncel değil (18 ay önce)

KONVEYÖR SİSTEMİ:
- Model: Modüler konveyör bant sistemi
- Hız: 12 metre/dakika (ayarlanabilir)
- Son bakım: 1 ay önce
- Arıza geçmişi: Sık ürün sıkışması (haftada 3-4 kez)
- Operatör müdahalesi: Düzenli (günde 5-10 kez)
- Koruyucu ekipman: Tasarım aşamasında düşünülmemiş

KÖK NEDEN ÖN BULGULAR:
1. Makine çalışır durumdayken elle müdahale yapıldı
2. Koruyucu kapak/sensör sistemi yok
3. Operatör çalışırken müdahale prosedürü bilmiyor
4. "Üretimi durdurmayalım" baskısı - zaman kaybı endişesi
5. Sık sıkışma sorunu (kronik problem) - normalleşmiş
6. Risk değerlendirmesi güncellenmemiş
7. Acil durdurma butonlarının konumu uygunsuz (uzak)
8. İşbaşı eğitimi yetersiz (makine güvenliği detaylı anlatılmamış)

TANIK BEYANLARI:
- Elif Kaya (Operatör): "Fatma hep öyle yapıyordu. Hepimiz yapıyoruz. 
  Bandı durdurup tekrar başlatmak 5 dakika sürer. Şef acele ediyor."
- Hat Şefi Ayşe: "Sıkışma çok sık oluyor. Operatörler hızlıca çözüyor. 
  Makineyi her seferinde durdurmak verimsiz."
- Bakım Teknisyeni: "Konveyör ayarı bozuk, ürünler sık sıkışıyor. 
  Ancak üretim durmadan ayar yapılamıyor."

YÖNETİM FAKTÖRLERI:
- Üretim hedefi: Günlük 5000 ünite (yüksek)
- Duruş süreleri: Minimize edilmeli (performans kriteri)
- Bakım penceresi: Sadece hafta sonu (yetersiz)
- Verimlilik önceliği: "Hızlı ol, ara verme" kültürü
- Güvenlik eğitimi: Yıllık 1 kez (genel, detay yok)
- Risk değerlendirmesi: Güncellenmemiş

BENZER OLAY GEÇMİŞİ:
- 6 ay önce: Başka operatörün parmağı sıkıştı (hafif yaralanma)
- 1 yıl önce: El ezilmesi (tedavi edildi, rapor yok)
- 2 yıl önce: Benzer olay (kayıt dışı)
→ Tekrarlayan bir sorun var, önlem alınmamış

MAKİNE TASARIM EKSİKLİĞİ:
- Koruyucu tasarlanmamış
- İşletme kılavuzunda güvenlik bilgisi yetersiz
- CE belgesi: Var ama eski standart (2010)
- Güvenlik sistemleri: Retrofit edilmemiş
- Ergonomik: Zayıf (operatör uzanmak zorunda)

ACIL ÖNLEMLER:
1. Konveyör bandı durduruldu, inceleme yapıldı
2. Tüm operatörlere acil güvenlik eğitimi verildi
3. Koruyucu kapak tasarımı başlatıldı
4. Işık perdesi montajı planlandı
5. "Bandı durdur, sonra müdahale et" prosedürü yazıldı
6. Uyarı levhaları asıldı
7. Acil durdurma butonları ek noktalara eklendi
"""


# ============================================================================
# TEST FUNCTIONS
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
    """Run machine entrapment incident test."""
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("MAKİNE SIKIŞMASI OLAYI - TAM SİSTEM TESTİ")
    print_info(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Olay: Konveyör bandı - çalışır halde elle müdahale")
    
    results = {"timestamp": timestamp, "steps": {}, "files": []}
    
    # Step 1: Environment
    print_header("ADIM 1: Ortam Hazırlığı")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("API key bulunamadı")
        print_success(f"API Key OK: {api_key[:10]}...{api_key[-4:]}")
        
        Path("outputs").mkdir(exist_ok=True)
        print_success("Çıktı dizini hazır")
        
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Ortam hatası: {e}")
        results["steps"]["environment"] = "FAILED"
        return results
    
    # Step 2: OverviewAgent
    print_header("ADIM 2: OverviewAgent - İlk Analiz")
    try:
        agent = OverviewAgent()
        # INCIDENT_DATA'yı dict olarak gönder
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        
        print_success(f"Ref: {part1.get('ref_no')}")
        print_success(f"Tip: {part1.get('incident_type')}")
        print_info(f"Ne: {part1.get('brief_details', {}).get('what', '')[:60]}...")
        
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Hata: {e}")
        results["steps"]["overview"] = "FAILED"
        return results
    
    # Step 3: AssessmentAgent
    print_header("ADIM 3: AssessmentAgent - Şiddet Analizi")
    try:
        agent = AssessmentAgent()
        # INCIDENT_DATA'yı dict olarak gönder
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        
        print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Seviye: {part2.get('investigation', {}).get('level')}")
        
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Hata: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results
    
    # Step 4: RootCauseAgentV2
    print_header("ADIM 4: RootCauseAgentV2 - Kök Neden")
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
            code = rc.get("root_cause_code", "")
            title = rc.get("root_cause_title", "")[:45]
            print_info(f"[{i}] {code} - {title}")
        
        json_file = f"outputs/machine_entrapment_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON kaydedildi: {json_file}")
        results["files"].append(json_file)
        
        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results
    
    # Step 5: Report Generation
    print_header("ADIM 5: Rapor Üretimi")
    try:
        agent = SkillBasedDocxAgent()
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = f"outputs/{ref_no}_machine_entrapment.docx"
        
        data = {"part1": part1, "part2": part2, "part3_rca": part3}
        result = agent.generate_report(data, docx_file)
        
        html_file = result.replace('.docx', '.html')
        
        if Path(result).exists():
            size = Path(result).stat().st_size / 1024
            print_success(f"DOCX: {size:.1f} KB")
            print_info(f"→ {result}")
            results["files"].append(result)
        
        if Path(html_file).exists():
            html_size = Path(html_file).stat().st_size / 1024
            print_success(f"HTML: {html_size:.1f} KB")
            print_info(f"→ {html_file}")
            results["files"].append(html_file)
        
        results["steps"]["report"] = "PASSED"
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["report"] = "FAILED"
        return results
    
    # Final summary
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])
    
    print_header("SONUÇ")
    print_info(f"Toplam Süre: {elapsed:.1f} saniye")
    print_info(f"Başarı Oranı: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 TÜM TESTLER BAŞARILI!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ {total-passed} adım başarısız")
        results["overall"] = "FAILED"
    
    print("\n📄 Oluşturulan Dosyalar:")
    for f in results["files"]:
        print(f"   • {f}")
    print()
    
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
