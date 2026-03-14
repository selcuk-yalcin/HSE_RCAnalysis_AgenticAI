"""
SENARYO 1: KİMYASAL YANMA KAZASI - ASİT SIÇRAMASI
=====================================================
Farklılıklar:
- Kimyasal madde maruziyeti (fiziksel kaza değil)
- Acil durum prosedürü eksikliği
- KKD kullanımı var AMA yetersiz kalite
- Eğitim var AMA pratik yok
- Risk değerlendirmesi var AMA güncel değil
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
from agents.skillbased_docx_agent import SkillBasedDocxAgent


def main():
    print("=" * 100)
    print("🧪 KİMYASAL YANMA SENARYOSU - ASİT SIÇRAMASI TESTİ")
    print("=" * 100)
    print()

    incident_summary = """
KAZA RAPORU - KİMYASAL YANMA (ASIT SIÇRAMASI)
==============================================

1. GENEL BİLGİLER
-----------------
Rapor No: CHM-2026-001-BURN
Tarih/Saat: 15.03.2026 / 14:30
Lokasyon: ABC Kimya Fabrikası, Asit Depolama Sahası, Tank 7 Dolum İstasyonu
Kazazede: Mehmet Yılmaz, 34 yaş, Kimya Teknisyeni
Şirket: ABC Kimya A.Ş.
Kıdem: 8 yıl (firmada), 5 yıl (mevcut pozisyonda)

2. OLAY ÖZETİ
-------------
Mehmet Yılmaz, %98 konsantrasyonlu sülfürik asit transferi sırasında hortum bağlantısının 
gevşemesi sonucu yüzüne ve göğsüne asit sıçraması olmuştur. Olay sonrası acil durum duşuna 
koşmuş ancak duşun basıncı yetersiz olduğu için etkili yıkama yapılamamıştır. 

3. ZAMAN ÇİZELGESİ
------------------
08:00 - Vardiya başlangıcı, toolbox meeting (Konu: Elektrik güvenliği - asit transferi DEĞİL)
09:00 - Tank 7'ye asit transferi için hazırlık başladı
09:30 - Pompa devreye alındı, ilk kontrol yapıldı
10:00 - Çay molası
10:15 - Transfer devam etti
14:25 - Hortum titreşimi fark edildi, operatör kontrol için yaklaştı
14:30 - Hortum bağlantısı gevşedi, asit sıçradı
14:31 - Acil durum duşuna koştu, yıkama başladı
14:32 - Duş basıncı yetersiz, operatör bağırdı
14:33 - İş arkadaşları yardıma geldi, yanındaki normal musluktan yıkama yapıldı
14:35 - 112 arandı, ilk yardım malzemeleri getirildi
14:50 - Ambulans geldi, hastaneye sevk

4. BULGULAR
-----------

4.1 Personel:
✅ Eğitim aldı: Temel İSG (16 saat), Kimyasal Güvenlik (8 saat) - 2025 Ocak
✅ Sağlık raporu güncel (Son muayene: Şubat 2026)
✅ MYK Belgesi: Kimya Operatörü Seviye 4 (Geçerli)
⚠️ Pratik acil durum tatbikatı: 2 yıl önce (2024 Mart)
❌ Asit transfer prosedürü pratik eğitimi: YOK
❌ Acil durum duş kullanım pratiği: YOK

4.2 KKD:
✅ Sağlandı: Kimyasal koruyucu gözlük, eldiven, önlük
⚠️ Kullanıldı: EVET ama...
❌ Gözlük kalitesi: CE belgeli ama asit sıçramasına YETERSIZ (yan koruma yok)
❌ Eldiven: Nitril (sülfürik aside karşı 10 dk koruma - yetersiz)
❌ Yüz siperi: YOK (risk değerlendirmesinde gerekli görülmüş ama tedarik edilmemiş)

4.3 Ekipman/Sistem:
❌ Acil durum duşu basıncı: Test edilmemiş (son test: 14 ay önce)
❌ Hortum bağlantısı: Orijinal parça değil, lokal imalat kullanılmış
❌ Titreşim sensörü: Var ama ARIZALI (2 haftadır bakım bekliyor)
⚠️ Transfer pompası: Periyodik bakımı yapılmış (1 hafta önce)

4.4 Yönetim Sistemi:
⚠️ Risk Değerlendirmesi: VAR ama 18 ay önce yapılmış (güncelleme: yıllık olmalı)
⚠️ İş İzin Belgesi: Dolduruluyor ama RUTIN olarak imzalanıyor (detaylı kontrol YOK)
❌ Acil Durum Planı: Var ama PERSONEL BİLMİYOR (teorik kaldı)
❌ Kritik ekipman test programı: Kağıt üzerinde var ama UYGULANMIYOR

4.5 Çevre:
- Sıcaklık: 28°C (sıcak hava)
- Rüzgar: Hafif (2-3 m/s)
- Gürültü: Yüksek (pompa sesleri ~85 dB)
- Aydınlatma: İyi

5. TANIKLARDAN ALINAN İFADELER
------------------------------
- Ali Kaya (Operatör): "Hortum titriyordu, Mehmet kontrol için yaklaştı. Birden sıçradı."
- Ayşe Demir (Vardiya Şefi): "Duş test programı vardı ama kimse uygulamıyordu, zaman yok diyorlardı."
- Fatma Yıldız (İSG Uzmanı): "Yüz siperi alım talebi 3 ay önce verildi, bütçe onayı bekleniyor."

6. İLK BULGULAR - KÖK NEDEN İPUÇLARI
-------------------------------------
❌ Acil durum ekipmanı test/bakım eksikliği
❌ KKD kalite/uygunluk problemi (ucuz tedarik)
❌ Pratik eğitim/tatbikat eksikliği (teoride kalıyor)
❌ Risk değerlendirmesi güncelleme eksikliği
❌ İş izin sistemi şekilsellik (rutin imza)
❌ Bakım yönetim sistemi zayıflığı (sensör arızası)
❌ Tedarik/satın alma kararları (maliyet odaklı, güvenlik ikinci planda)

7. YARALANMA
------------
- 2. derece kimyasal yanık (yüz, boyun, göğüs)
- Her iki gözde irritasyon
- Tedavi süresi: 45 gün (tahmini)
- Kalıcı hasar riski: Var (cilt lekesi, göz problemleri)
"""

    incident_data = {
        "ref_no": "CHM-2026-001-BURN",
        "reported_by": "Vardiya Amiri",
        "date_time": "15.03.2026 14:30",
        "description": incident_summary,
        "injury_description": "2. derece kimyasal yanık (yüz, boyun, göğüs), göz irritasyonu"
    }

    print("\n" + "="*100)
    print("📋 ADIM 1: OVERVIEW AGENT - OLAYI ANALİZ ET")
    print("="*100 + "\n")
    
    overview_agent = OverviewAgent()
    
    try:
        overview_result = overview_agent.process_initial_report(incident_data)
        
        print("\n✅ Overview Analizi Tamamlandı!")
        print(f"📊 Olay Tipi: {overview_result.get('incident_type', 'N/A')}")
        print(f"🏷️ Referans No: {overview_result.get('ref_no', 'N/A')}")
        
    except Exception as e:
        print(f"❌ HATA (Overview): {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("📋 ADIM 2: ASSESSMENT AGENT - RİSK DEĞERLENDİR")
    print("="*100 + "\n")
    
    assessment_agent = AssessmentAgent()
    
    try:
        assessment_result = assessment_agent.assess_incident(overview_result, incident_data)
        
        print("\n✅ Assessment Analizi Tamamlandı!")
        print(f"⚠️ Ciddiyet: {assessment_result.get('actual_potential_harm', 'N/A')}")
        print(f"� RIDDOR: {assessment_result.get('riddor_reportable', 'N/A')}")
        
    except Exception as e:
        print(f"❌ HATA (Assessment): {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("📋 ADIM 3: ROOT CAUSE AGENT V2 - KÖK NEDEN ANALİZİ (5-WHY)")
    print("="*100 + "\n")
    
    rootcause_agent = RootCauseAgent()
    
    try:
        root_cause_result = rootcause_agent.analyze_root_causes(
            overview_result, 
            assessment_result, 
            incident_data
        )
        
        print("\n✅ Kök Neden Analizi Tamamlandı!")
        
        branches = root_cause_result.get('analysis_branches', [])
        root_causes = root_cause_result.get('final_root_causes', [])
        
        print(f"\n🌳 Toplam {len(branches)} Ana Dal Tespit Edildi")
        print(f"🎯 Toplam {len(root_causes)} Kök Neden Bulundu")
        
        if root_causes:
            print("\n" + "="*100)
            print("KÖK NEDENLER:")
            print("="*100)
            for i, rc in enumerate(root_causes, 1):
                print(f"\n{i}. [{rc.get('code', '?')}] {rc.get('name', 'N/A')}")
                print(f"   → {rc.get('description', '')}")
        
        if branches:
            print("\n" + "="*100)
            print("DAL DETAYLARI:")
            print("="*100)
            for i, branch in enumerate(branches, 1):
                print(f"\n{'='*80}")
                print(f"DAL {i}:")
                print(f"Doğrudan Neden: {branch.get('direct_cause', {}).get('description', 'N/A')}")
                print(f"Kök Neden: {branch.get('root_cause', {}).get('description', 'N/A')}")
                
                why_chain = branch.get('five_why_chain', [])
                if why_chain:
                    print(f"\n5-WHY ZİNCİRİ:")
                    for j, why in enumerate(why_chain, 1):
                        print(f"  WHY {j}: {why.get('why', 'N/A')}")
                        print(f"      → {why.get('because', 'N/A')}")
        
        # Sonuçları kaydet
        output_dir = Path("outputs/chemical_burn_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(output_dir / f"overview_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(overview_result, f, ensure_ascii=False, indent=2)
        
        with open(output_dir / f"assessment_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(assessment_result, f, ensure_ascii=False, indent=2)
        
        with open(output_dir / f"rootcause_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(root_cause_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n📁 JSON Sonuçları kaydedildi: {output_dir}")
        
        # ============================================================================
        # HTML/DOCX RAPOR OLUŞTURMA
        # ============================================================================
        print("\n" + "="*100)
        print("📄 ADIM 4: TAM RAPOR OLUŞTURULUYOR (HTML + DOCX)...")
        print("="*100 + "\n")
        
        docx_agent = SkillBasedDocxAgent()
        
        try:
            # Rapor için veri hazırlama
            investigation_data = {
                "part1": overview_result,
                "part2": assessment_result,
                "part3_rca": root_cause_result
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/chemical_burn_test/chemical_burn_report_{timestamp}.docx"
            
            print("🤖 AI tam rapor oluşturuyor (Claude Sonnet 4.5 ile)...")
            docx_path = docx_agent.generate_report(investigation_data, output_path)
            
            # HTML de otomatik oluşturulacak
            html_path = docx_path.replace('.docx', '.html')
            
            if Path(docx_path).exists():
                print(f"\n✅ RAPORLAR BAŞARIYLA OLUŞTURULDU!")
                print(f"📄 DOCX Rapor: {docx_path}")
                if Path(html_path).exists():
                    print(f"📄 HTML Rapor: {html_path}")
            else:
                print(f"⚠️ Rapor oluşturulamadı")
                
        except Exception as e:
            print(f"❌ HATA (DOCX/HTML Rapor): {str(e)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ HATA (RootCause): {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("✅ KİMYASAL YANMA SENARYOSU TESTİ TAMAMLANDI!")
    print("  📊 JSON raporlar oluşturuldu")
    print("  📄 HTML tam rapor oluşturuldu")
    print("  📄 DOCX tam rapor oluşturuldu")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
