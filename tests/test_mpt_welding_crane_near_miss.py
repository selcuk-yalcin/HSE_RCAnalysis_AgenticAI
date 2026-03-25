"""
SENARYO: KAYNAK ATÖLYESİ MOBİL VİNÇ RAMAK KALA OLAYI - MALZEMENİN HASAR GÖRMESİ
===============================================================================
Rapor No: 03-26
Tarih: 21.01.2026 - 22.03 (Ramak Kala)
Olay Yeri: MPT - Taşlama İşlemi (Murat Araz)
Olay Türü: İş/Üretim - Ramak Kala

OLAY DETAYI (Rapordan):
-----------------------
Kaynak atölyesinde gerçekleştirilen taşlama işlemi sırasında oluşan kıvılcım
ve sıcak partiküller, aynı kapalı alan içerisinde bulunan seyyar oksi-asetilen
tüpüne ulaşmıştır. Yapılan incelemede, oksi-asetilen tüpünün manometre
bağlantı noktasında gaz kaçağı bulunduğu tespit edilmiştir. Taşlama işlemi
esnasında yayılan kıvılcımların bu bağlantı noktasına temas etmesi sonucu tüp
üzerinde alevlenme meydana gelmiştir.

Söz konusu alevlenme, taşlama işlemini gerçekleştiren çalışan tarafından
yaklaşık 4 dakika sonra fark edilmiş, çalışanın hızlı müdahalesi ile boğma
yöntemi kullanılarak yangın kontrol altına alınmış ve söndürülmüştür.

Olay sırasında herhangi bir yaralanma meydana gelmemiştir; ancak durum,
potansiyel olarak ciddi sonuçlar doğurabilecek bir yangın ve patlama riski
barındırmaktadır.

ÖNEMLİ NOKTALAR:
- Zaman Kaybı: Potansiyel Zarar (4 dakika geç fark edilme)
- Hafif Yaralanma: Hayır
- Orta Hasar: Var (oksi-asetilen tüpü, ekipman hasarı)
- Ölüm: Hayır
- Malzeme: Var (tüp ve çevre ekipmanı hasar görmüş)
- Çoklu Ölüm: Hayır
- İş Durdurma: Hayır
- Yüksek Hasar: Hayır

EK BİLGİLER:
- Fotoğraflar mevcut
- Tanık ifadeleri var
- Medikal rapor gerekmedi (yaralanma yok)

BULGULAR:
✅ Kişisel yaralanma YOK
❌ Oksi-asetilen tüpü manometre bağlantısında gaz kaçağı
❌ Kapalı alanda seyyar oksi-asetilen tüpü taşlama işlemi yakınında
❌ 4 dakika geç fark edilme (görüş açısı/duman/kıvılcım yoğunluğu)
❌ Çalışma alanı izolasyonu/bariyerleme YOK
⚠️ Yangın ve patlama riski (potansiyel ciddi sonuçlar)
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
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent
from agents.unified_analysis_pipeline import MongoDBCache, AnalysisCache


def main():
    print("=" * 100)
    print("🔥 KAYNAK ATÖLYESİ MOBİL VİNÇ RAMAK KALA OLAYI - OKSİ-ASETİLEN TÜP YANGINI")
    print("=" * 100)
    print()

    incident_summary = """
RAMAK KALA RAPORU - KAYNAK ATÖLYESİ OKSİ-ASETİLEN TÜP YANGINI
=============================================================

RAPOR BİLGİLERİ:
- Rapor No: 03-26
- Rapor Tarihi: 9.02.2026
- Olay: Yangın - Ramak Kala
- Olay Yeri: MPT Atölye
- Olay Bölgesi: Taşlama İşlemi
- Aktivite: Taşlama İşlemi
- Bölge Sorumlusu: Murat Araz

OLAY TARİHİ VE SAATİ:
21.01.2026 - 22:03 (gece vardiyası)

OLAY SONUÇ TİPİ:
✅ Ramak Kala (Near Miss)
❌ LTI (Kayıp İş Günü Yaralanması)
❌ Maddi Hasarlı
❌ İlk Yardım
❌ İş/Üretim
❌ Seyahat
❌ Ulaşım

ARAŞTIRMA SEVİYESİ:
✅ Seviye A (Yüksek) - Potansiyel ciddi sonuçlar (yangın/patlama riski)
❌ Seviye B (Orta)

OLAY TÜRÜ:
✅ İş/Üretim
❌ Ofis
❌ Seyahat
❌ Ulaşım

MEVCUT ZARAR:
- Zaman Kaybı: ❌
- Potansiyel Zarar: ✅ (4 dakika geç fark edilme)
- Hafif Yaralanma: ❌
- Orta Hasar: ✅ (tüp + ekipman hasarı)
- Ölüm: ❌
- Malzeme: ✅ (hasarlı tüp + çevre ekipmanları)
- Çoklu Ölüm: ❌
- İş Durdurma: ❌
- Yüksek Hasar: ❌

MADDI ZARAR:
Dökülme: Hayır
Dökülme Miktarı: -

ÇEVRE OLAYI:
Dökülme: Hayır
Yangın: Hayır (kontrol altına alındı)
Patlama: Hayır

DETAYLI AÇIKLAMA:
=================

1. OLAY SÜRECİ
--------------
Kaynak atölyesinde gerçekleştirilen taşlama işlemi sırasında oluşan kıvılcım ve sıcak 
partiküller, aynı kapalı alan içerisinde bulunan seyyar oksi-asetilen tüpüne ulaşmıştır. 

Yapılan incelemede, oksi-asetilen tüpünün manometre bağlantı noktasında gaz kaçağı 
bulunduğu tespit edilmiştir. Taşlama işlemi esnasında yayılan kıvılcımların bu bağlantı 
noktasına temas etmesi sonucu tüp üzerinde alevlenme meydana gelmiştir.

Söz konusu alevlenme, taşlama işlemini gerçekleştiren çalışan tarafından yaklaşık 
4 dakika sonra fark edilmiş, çalışanın hızlı müdahalesi ile boğma yöntemi kullanılarak 
yangın kontrol altına alınmış ve söndürülmüştür.

Olay sırasında herhangi bir yaralanma meydana gelmemiştir; ancak durum, potansiyel 
olarak ciddi sonuçlar doğurabilecek bir yangın ve patlama riski barındırmaktadır.

2. ZAMAN ÇİZELGESİ
------------------
21.01.2026, 22:00 - Taşlama işlemi başlatıldı (gece vardiyası)
22:01 - Kıvılcımlar oksi-asetilen tüpüne ulaşmaya başladı
22:03 - Manometre bağlantı noktasındaki gaz kaçağı ile kıvılcımlar temas etti
22:03 - Tüp üzerinde alevlenme meydana geldi
22:07 - Çalışan alevlenmeyi fark etti (4 dakika sonra)
22:08 - Çalışan boğma yöntemi ile yangını söndürmeye başladı
22:10 - Yangın kontrol altına alındı ve söndürüldü
22:12 - Olay rapor edildi
22:30 - Güvenlik ekibi ve vardiya amiri olay yerine geldi

3. KRİTİK BULGULAR
------------------

3.1 Ekipman/Sistem:
❌ Oksi-asetilen tüpü manometre bağlantı noktasında gaz kaçağı (KRİTİK)
❌ Seyyar tüp taşlama işlemi alanında (güvensiz konum)
❌ Kapalı alan - yetersiz havalandırma
❌ Alevlenmeyi erken tespit sistemi YOK (duman/alev dedektörü)
✅ Çalışan yangın söndürme eğitimi almış (boğma yöntemi kullandı)

3.2 İşlem/Prosedür:
❌ Taşlama ve oksi-asetilen tüpü aynı kapalı alanda (bariyerleme YOK)
❌ Güvenli mesafe kuralı ihlali (kıvılcımlar tüpe ulaşabildi)
❌ Sıcak işlem izin sistemi kontrolü eksik
❌ Risk değerlendirmesi: Taşlama + kapalı alan + gaz kaçağı senaryosu değerlendirilmemiş

3.3 Organizasyonel:
❌ Tüp periyodik kontrol/bakım sistemi eksikliği (gaz kaçağı önceden tespit edilemedi)
❌ Sıcak işlemler için alan izolasyonu standardı YOK
❌ Çalışma öncesi alet/ekipman kontrol listesi uygulanmıyor
⚠️ 4 dakika geç fark edilme - görünürlük/dikkatlendirme sorunu

3.4 İnsan Faktörü:
✅ Çalışan yangın söndürme konusunda eğitimli ve hızlı müdahale etti
❌ Çalışma öncesi tüp kontrolü yapılmadı (gaz kaçağı fark edilmedi)
❌ Taşlama sırasında çevre alanı sürekli gözlemleme yapılmadı (4 dakika)

4. HASAR/SONUÇ
--------------
- Kişisel yaralanma: YOK ✅
- Ekipman hasarı: Oksi-asetilen tüpü hasarlı (manometre bağlantı noktası)
- Malzeme hasarı: Çevre ekipmanlarında yanma/is lekeleri
- Potansiyel risk: YÜKSEK (patlama riski, çoklu ölüm riski)
- İş durumu: Operasyon geçici durduruldu, ekipman değiştirildi

5. RAMAK KALA DEĞERLENDİRMESİ
-----------------------------
POTANSİYEL CİDDİ SONUÇLAR:
⚠️ Yangın: Kapalı alanda kontrol dışı yangın riski
⚠️ Patlama: Oksi-asetilen tüpü patlaması riski
⚠️ Çoklu yaralanma/ölüm: Patlama durumunda atölyede bulunan tüm çalışanlar risk altında
⚠️ Tesis hasarı: Atölye binası ve çevre ekipmanları ciddi hasar görebilirdi

NEDEN RAMAK KALA?
✅ Çalışanın hızlı ve doğru müdahalesi (boğma yöntemi)
✅ Yangının henüz tüp içine sıçramaması
✅ Patlama olmaması

6. EK BİLGİLER
--------------
✅ Fotoğraflar: Mevcut (hasarlı tüp, alevlenme izi, çevre ekipmanları)
✅ Tanık ifadeleri: Vardiya arkadaşları tanık (3 kişi)
❌ Medikal rapor: Gerekmedi (yaralanma yok)
Diğer: Hasarlı tüp emniyet ekibi tarafından izole edildi ve imha için işaretlendi
"""

    incident_data = {
        "ref_no": "03-26",
        "report_date": "9.02.2026",
        "incident_date": "21.01.2026",
        "incident_time": "22:03",
        "incident_type": "Ramak Kala (Near Miss)",
        "location": "MPT Atölye - Taşlama İşlemi Alanı",
        "activity": "Taşlama İşlemi",
        "reported_by": "Murat Araz (Bölge Sorumlusu)",
        "description": incident_summary,
        "injury_description": "Kişisel yaralanma yok. Oksi-asetilen tüpü manometre bağlantısında hasar, çevre ekipmanlarında yanma lekeleri. Potansiyel patlama/yangın riski (ramak kala).",
        "potential_severity": "YÜKSEK (patlama/çoklu ölüm riski)",
        "witnesses": ["Vardiya arkadaşı 1", "Vardiya arkadaşı 2", "Vardiya arkadaşı 3"],
        "photos_available": True,
        "investigation_level": "Seviye A (Yüksek)"
    }

    print("\n" + "="*100)
    print("📋 ADIM 1: OVERVIEW AGENT - RAMAK KALA OLAYINI ANALİZ ET")
    print("="*100 + "\n")

    overview_agent = OverviewAgent()

    try:
        overview_result = overview_agent.process_initial_report(incident_data)

        print("\n✅ Overview Analizi Tamamlandı!")
        print(f"📊 Olay Tipi: {overview_result.get('incident_type', 'N/A')}")
        print(f"🏷️ Referans No: {overview_result.get('ref_no', 'N/A')}")
        print(f"⚠️ Ciddiyet: Ramak Kala (Potansiyel Patlama/Çoklu Ölüm Riski)")

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
        print(f"📋 RIDDOR: {assessment_result.get('riddor_reportable', 'N/A')}")
        print(f"🔥 Ramak Kala Değerlendirmesi: Potansiyel patlama/yangın riski")

    except Exception as e:
        print(f"❌ HATA (Assessment): {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("📋 ADIM 3: ROOT CAUSE AGENT V2 - KÖK NEDEN ANALİZİ (5-WHY)")
    print("="*100 + "\n")

    rootcause_agent = RootCauseAgentV2(use_rag=True)

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
        output_dir = Path("outputs/mpt_welding_near_miss")
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
            investigation_data = {
                "part1": overview_result,
                "part2": assessment_result,
                "part3_rca": root_cause_result
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/mpt_welding_near_miss/ramak_kala_report_{timestamp}.docx"

            print("🤖 AI tam rapor oluşturuyor (Claude Sonnet 4.5 ile)...")
            docx_path = docx_agent.generate_report(investigation_data, output_path)

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
    print("✅ KAYNAK ATÖLYESİ RAMAK KALA SENARYOSU TESTİ TAMAMLANDI!")
    print("  📊 JSON raporlar oluşturuldu")
    print("  📄 HTML tam rapor oluşturuldu")
    print("  📄 DOCX tam rapor oluşturuldu")
    print("="*100 + "\n")
    
    # ============================================================
    # CACHE'E KAYDET (MongoDB veya Disk)
    # ============================================================
    print("\n" + "="*100)
    print("💾 CACHE'E KAYIT")
    print("="*100 + "\n")
    
    try:
        # MongoDB cache'e yaz
        print("🔍 MongoDB cache'e yazılıyor...")
        cache = MongoDBCache()
        
        analysis_result = {
            "source": "mpt_welding_near_miss",
            "timestamp": datetime.now().isoformat(),
            "incident_ref": incident_data.get("ref_no"),
            "overview": overview_result,
            "assessment": assessment_result,
            "root_cause_analysis": root_cause_result
        }
        
        cache.set(incident_data, analysis_result)
        print("✅ MongoDB cache'e başarıyla yazıldı!")
        
        stats = cache.get_stats()
        print(f"   📊 Cache Stats:")
        print(f"      Hits: {stats['hits']}")
        print(f"      Misses: {stats['misses']}")
        print(f"      Money Saved: ${stats['saved_cost']:.2f}")
        
    except Exception as e:
        print(f"⚠️  MongoDB cache yazma hatası: {e}")
        print("   Disk cache'e yazılıyor...")
        
        try:
            cache = AnalysisCache()
            analysis_result = {
                "source": "mpt_welding_near_miss",
                "timestamp": datetime.now().isoformat(),
                "incident_ref": incident_data.get("ref_no"),
                "overview": overview_result,
                "assessment": assessment_result,
                "root_cause_analysis": root_cause_result
            }
            
            cache.set(incident_data, analysis_result)
            print("✅ Disk cache'e başarıyla yazıldı!")
        except Exception as e2:
            print(f"❌ Cache yazma hatası: {e2}")
    
    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    main()
