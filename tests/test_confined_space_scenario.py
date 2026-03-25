"""
SENARYO 2: CONFINED SPACE - OKSİJEN EKSİKLİĞİ BAYILMA
======================================================
Farklılıklar:
- İzinsiz giriş (Confined Space Permit yok)
- Atmosfer testi yapılmamış
- Gözcü/yardımcı personel yok
- Kurtarma planı yok
- Birden fazla kazazede (kurtarmaya girenler de etkilendi)
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
    print("🚨 CONFINED SPACE SENARYOSU - OKSİJEN EKSİKLİĞİ BAYILMA TESTİ")
    print("=" * 100)
    print()

    incident_summary = """
KAZA RAPORU - CONFINED SPACE (KAPALI ALAN) - OKSİJEN EKSİKLİĞİ
===============================================================

1. GENEL BİLGİLER
-----------------
Rapor No: CS-2026-002-OXYGEN
Tarih/Saat: 18.03.2026 / 11:45
Lokasyon: DEF Atıksu Arıtma Tesisi, Çamur Depolama Tankı #3 (5m çap, 8m derinlik)
Kazazede 1: Ahmet Çelik, 29 yaş, Bakım Teknisyeni (birincil)
Kazazede 2: Hasan Öztürk, 42 yaş, Vardiya Amiri (kurtarmaya girdi)
Kazazede 3: Kemal Aydın, 35 yaş, Operatör (kurtarmaya girdi)
Şirket: DEF Çevre Teknolojileri A.Ş.

2. OLAY ÖZETİ
-------------
Bakım teknisyeni Ahmet Çelik, tank içinde pompa arızasını kontrol etmek için izinsiz 
girmiş ve ~3 metre derinlikte bayılmıştır. Kurtarmaya giren vardiya amiri Hasan Öztürk 
da oksijen eksikliği nedeniyle bayılmış, ardından operatör Kemal Aydın da etkilenmiştir. 
İtfaiye ekipleri 3 kişiyi de kurtarmıştır.

3. ZAMAN ÇİZELGESİ
------------------
07:00 - Vardiya başlangıcı, normal operasyon
09:30 - Tank #3 çamur pompası alarm verdi (tıkanma şüphesi)
09:45 - Ahmet Çelik arızayı incelemeye gitti
10:00 - Tank dış gözlemini yaptı, "içeriye bakmam lazım" dedi
10:15 - Ekip liderinden sözlü onay istedi, lider "dikkatli ol" dedi
10:20 - Ahmet tek başına tank kapağını açtı
10:25 - Merdivenden aşağı inmeye başladı (atmosfer testi YOK, gözcü YOK)
10:28 - 3 metre derinlikte bayıldı, merdivenden düştü
10:30 - İş arkadaşları seslendi, yanıt alamayınca endişelendi
10:32 - Hasan Öztürk (amir) tank başına geldi, Ahmet'i gördü
10:33 - Hasan kurtarmak için atladı (KKD YOK, atmosfer testi YOK)
10:34 - Hasan da bayıldı, tank dibine düştü
10:36 - Kemal Aydın yardıma koştu, yarı yolda bayıldı
10:37 - Diğer çalışanlar 112 ve itfaiyeyi aradı
10:40 - Tesiste acil durum bildirimi yapıldı
10:55 - İtfaiye SCBA (solunum cihazı) ile tank içine girdi
11:00 - İlk iki kişi çıkarıldı (Ahmet ve Hasan)
11:05 - Üçüncü kişi çıkarıldı (Kemal)
11:10 - Üçüne de CPR uygulandı, ambulanslar geldi
11:20 - Üç kazazede de hastaneye sevk

4. BULGULAR
-----------

4.1 Personel Bilgileri:

Ahmet Çelik:
✅ Eğitim: Temel İSG (16 saat), Atıksu Prosesleri (24 saat) - 2025
❌ Confined Space Eğitimi: YOK
❌ Atmosfer Test Cihazı Kullanımı: YOK
✅ Sağlık raporu güncel
⚠️ Kıdem: 2 yıl (deneyimli sayılır ama confined space'te YENİ)

Hasan Öztürk:
✅ Eğitim: Vardiya Amiri eğitimleri tamamlanmış
❌ Kurtarma Eğitimi: YOK (teorik var, pratik YOK)
❌ SCBA Kullanımı: Bilmiyor
⚠️ Kahramanlık refleksi: "Adamımı kurtarmalıyım" - eğitimsiz girdi

Kemal Aydın:
❌ Acil Durum Prosedürü: Bilmiyor
❌ Confined Space Tehlikeleri: Farkında değil

4.2 Ekipman/Sistem:

❌ Atmosfer Test Cihazı: Tesiste VAR ama KİLİTLİ DOLAPTA (anahtarı İSG uzmanında)
❌ SCBA (Solunum Cihazı): YOK (bütçe kısıtı)
❌ Havalandırma Fanı: Var ama ARIZALI (6 ay bakım bekliyor)
❌ Tripod/Kurtarma Ekipmanı: YOK
❌ Emniyet Kemeri/Halat: Var ama depoda, kimse bilmiyor
⚠️ İkaz Levhası: "Confined Space - İzinsiz Giriş Yasaktır" var ama SİLİK

4.3 Yönetim Sistemi:

❌ Confined Space Permit (Giriş İzni): Sistem VAR ama UYGULANMIYOR
❌ Atmosfer Test Protokolü: Kağıt üzerinde var ama personel BİLMİYOR
❌ Kurtarma Planı: YOK (hiç hazırlanmamış)
❌ Acil Durum Tatbikatı: 3 yıldır YAPILMAMIŞ
⚠️ Risk Değerlendirmesi: Confined space riski TESPİT EDİLMİŞ ama kontroller eksik
⚠️ Sözlü İzin Kültürü: "Dikkatli ol" yeterli görülüyor, yazılı prosedür yok

4.4 Atmosfer Analizi (İtfaiye sonrası):

- O2: %11 (Normal: %20.9) → OKSİJEN EKSİKLİĞİ kritik!
- H2S: 45 ppm (Limit: 10 ppm) → ZEHİRLİ GAZ var
- CH4: %2.1 (Patlama alt limiti: %5) → Henüz patlama riski yok
- CO: 15 ppm (Limit: 50 ppm) → Kabul edilebilir seviye

5. TANIKLARDAN ALINAN İFADELER
------------------------------
- Mehmet Kara (Operatör): "Ahmet 'hemen hallederim' dedi, biz de itiraz etmedik."
- Fatih Yılmaz (Ekip Lideri): "Sözlü onay verdim ama permit doldurmadık, işi hızlı bitirmek istedik."
- Zeynep Arslan (İSG Uzmanı): "Atmosfer test cihazını kilitli tutuyorum çünkü daha önce kaybolmuştu."
- Selim Demir (Tesis Müdürü): "Bütçe kısıtı var, SCBA ve tripod için onay alamadık."

6. İLK BULGULAR - KÖK NEDEN İPUÇLARI
-------------------------------------
❌ Confined Space Permit sistemi var ama uygulanmıyor (şekilsellik)
❌ Atmosfer testi yapılmamış (cihaz erişilemez)
❌ Kurtarma ekipmanı yetersiz/erişilemez (bütçe, organizasyon)
❌ Eğitim eksikliği (confined space, atmosfer testi, kurtarma)
❌ Gözcü/yardımcı personel kültürü yok
❌ Sözlü onay kültürü (yazılı prosedür atlanıyor)
❌ Hızlı iş bitirme baskısı (güvenlik ikinci planda)
❌ Kahramanlık refleksi (eğitimsiz kurtarma girişimi)
❌ Acil durum tatbikatı yapılmıyor
❌ Yönetim taahhüdü zayıf (bütçe kısıtı, ekipman eksikliği)

7. YARALANMA/SONUÇ
------------------
Ahmet Çelik: 
- Bilinç kaybı, hipoksi (oksijen eksikliği)
- Beyin hasarı riski var
- Yoğun bakımda takip
- Durum: KRİTİK

Hasan Öztürk:
- Hipoksi, baş travması (düşme)
- Bilinç kaybı
- Durum: AĞIR

Kemal Aydın:
- Hafif hipoksi
- Bilinç yerinde
- Durum: ORTA

Olası Sonuç: 1 kişi kalıcı hasar, 3 kişi psikolojik travma
"""

    incident_data = {
        "ref_no": "CS-2026-002-OXYGEN",
        "reported_by": "Güvenlik Görevlisi",
        "date_time": "18.03.2026 11:45",
        "description": incident_summary,
        "injury_description": "3 kişi oksijen eksikliği, 2 kişi yoğun bakımda"
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
        output_dir = Path("outputs/confined_space_test")
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
            
            output_path = f"outputs/confined_space_test/confined_space_report_{timestamp}.docx"
            
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
    print("✅ CONFINED SPACE SENARYOSU TESTİ TAMAMLANDI!")
    print("  📊 JSON raporlar oluşturuldu")
    print("  📄 HTML tam rapor oluşturuldu")
    print("  📄 DOCX tam rapor oluşturuldu")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
