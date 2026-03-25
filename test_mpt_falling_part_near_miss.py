"""
SENARYO: MPT TEST SAHASI SARMAL KAPI DÜŞEN PARÇA RAMAK KALA OLAYI
===================================================================
Rapor No: 02-26
Tarih: 20.01.2026 - 09:10
Olay Yeri: MPT Test
Olay Türü: Ramak Kala (Near Miss) - İş/Üretim
Bölge Sorumlusu: Hakan Sevil

OLAY DETAYI (Rapordan):
-----------------------
MPT Test Sahasında bulunan sarmal kapının kapatılması işlemi sırasında, 
kapının üst mekanizmasından anormal sesler gelmiştir. Seslerin hemen ardından, 
kapının üst bölümünde yer alan bir parçanın yerinden koparak düştüğü tespit 
edilmiştir.

Kopan parça, olay esnasında test sahasında bulunan çalışanın yaklaşık 2 metre 
yakınına düşmüştür. Olay sırasında herhangi bir yaralanma meydana gelmemiştir. 
Ancak olay, potansiyel yaralanma riski (near miss) oluşturmuştur.

ÖNEMLİ NOKTALAR:
- Olay Sonuç Tipi: Ramak Kala ☑
- Araştırma Seviyesi: Seviye A (Yüksek) ☑
- Olay Türü: İş/Üretim ☑

MEVCUT/POTANSİYEL ZARAR:
- Zaman Kaybı: Var ☑
- Potansiyel Zarar: Var ☑ (2 metre yakınlık - kafa/omuz yaralanması riski)
- Ölüm: Var ☑ (potansiyel ölümcül yaralanma)
- Orta Hasar: Var ☑
- Malzeme: Var ☑ (kopan parça)

EK BİLGİLER:
- Fotoğraflar mevcut ☑
- Tanık ifadeleri var ☑
- Medikal rapor gerekmedi (yaralanma yok)

BULGULAR:
✅ Kişisel yaralanma YOK (sadece 2 metre mesafe farkıyla)
❌ Sarmal kapı üst mekanizması bakım/kontrol eksikliği
❌ Anormal ses fark edilmesine rağmen işlem devam etmiş
❌ Potansiyel ölüm/ciddi yaralanma riski (baş/boyun bölgesine düşme)
❌ Periyodik bakım sistemi yetersiz
⚠️ Çalışan şanslı (2 metre mesafe kritik)
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
    print("⚠️ MPT TEST SAHASI SARMAL KAPI DÜŞEN PARÇA RAMAK KALA OLAYI")
    print("=" * 100)
    print()

    incident_summary = """
RAMAK KALA RAPORU - SARMAL KAPI DÜŞEN PARÇA OLAYI
==================================================

RAPOR BİLGİLERİ:
- Rapor No: 02-26
- Rapor Tarihi: 21.01.2026
- Olay: Kritik Ekipman Hasarı
- Olay Yeri: MPT Test
- Olay Bölgesi: MPT
- Aktivite: Test
- Bölge Sorumlusu: Hakan Sevil

OLAY TARİHİ VE SAATİ:
20.01.2026 - 09:10 (sabah vardiyası)

OLAY SONUÇ TİPİ:
❌ LTI (Kayıp İş Günü Yaralanması)
❌ Maddi Hasarlı
❌ İlk Yardım
✅ Ramak Kala (Near Miss) - KRİTİK
❌ İş/Üretim
❌ Seyahat
❌ Ulaşım

ARAŞTIRMA SEVİYESİ:
✅ Seviye A (Yüksek) - Potansiyel ölüm/ciddi yaralanma riski
❌ Seviye B (Orta)

OLAY TÜRÜ:
✅ İş/Üretim
❌ Ofis
❌ Seyahat
❌ Ulaşım

MEVCUT ZARAR:
- Zaman Kaybı: ✅
- Potansiyel Zarar: ✅ (2 metre yakınlık - baş/omuz bölgesi riski)
- Hafif Yaralanma: ❌
- Orta Hasar: ✅ (sarmal kapı mekanizması)
- Ölüm: ✅ (potansiyel ölümcül yaralanma riski)
- Malzeme: ✅ (kopan metal parça)
- Çoklu Ölüm: ❌
- İş Durdurma: ❌
- Yüksek Hasar: ❌

ÇEVRE OLAYI:
Dökülme: Hayır
Yangın: Hayır
Patlama: Hayır

DETAYLI AÇIKLAMA:
=================

1. OLAY SÜRECİ
--------------
MPT Test Sahasında bulunan sarmal kapının kapatılması işlemi sırasında, kapının üst 
mekanizmasından anormal sesler gelmiştir. Seslerin hemen ardından, kapının üst bölümünde 
yer alan bir parçanın yerinden koparak düştüğü tespit edilmiştir.

Kopan parça, olay esnasında test sahasında bulunan çalışanın yaklaşık 2 metre yakınına 
düşmüştür. Olay sırasında herhangi bir yaralanma meydana gelmemiştir. Ancak olay, 
potansiyel yaralanma riski (near miss) oluşturmuştur.

POTANSİYEL ETKİ ANALİZİ:
- Parça ağırlığı: Orta-ağır metal parça (mekanizma parçası)
- Düşme yüksekliği: ~3-4 metre (sarmal kapı üst mekanizması)
- Düşme mesafesi: Çalışana 2 metre yakınlık
- Potansiyel vuruş bölgesi: Baş, omuz, sırt bölgesi
- Sonuç olabilirdi: Kafatası kırığı, omurga hasarı, iç kanama, ölüm

2. ZAMAN ÇİZELGESİ
------------------
20.01.2026, 09:05 - Çalışan test sahasına giriş yaptı
09:08 - Sarmal kapının kapatılması işlemi başlatıldı
09:09 - Kapı üst mekanizmasından anormal sesler duyulmaya başladı
09:10 - Anormal sesler devam etti, çalışan sesi fark etti ama işlem devam etti
09:10:15 - Metal parça üst mekanizmadan koptu
09:10:16 - Parça çalışanın 2 metre yakınına düştü
09:10:20 - Çalışan durumu fark etti ve güvenli mesafeye çekildi
09:11 - Kapı mekanizması durduruldu
09:15 - Olay vardiya amirine rapor edildi
09:30 - Güvenlik ekibi ve bölge sorumlusu olay yerine geldi
10:00 - Kapı kullanım dışı bırakıldı, alternatif giriş/çıkış yolu belirlendi

3. KRİTİK BULGULAR
------------------

3.1 Ekipman/Sistem:
❌ Sarmal kapı üst mekanizması: Bakım/kontrol eksikliği (KRİTİK)
❌ Metal parça bağlantısı: Aşınma/gevşeme tespit edilememiş
❌ Anormal ses önceden fark edilmemiş (periyodik kontrol eksikliği)
❌ Kapı güvenlik sensörleri: Mekanik arıza tespiti yok
✅ Kapı çalışma prensibi: Normal (sadece üst mekanizma parçası sorunlu)

3.2 İşlem/Prosedür:
❌ Anormal ses duyulmasına rağmen işlem durdurulmadı (kritik hata)
❌ "Sesli uyarı = Tehlike" farkındalığı eksik
❌ Çalışma öncesi kapı mekanizması görsel/işitsel kontrol yapılmıyor
❌ Sarmal kapı kullanım prosedüründe "anormal ses" durumunda acil durdurma talimatı yok

3.3 Organizasyonel:
❌ Sarmal kapı periyodik bakım sistemi yetersiz (üst mekanizma kontrolü eksik)
❌ Bakım kayıtları: Son detaylı bakım tarihi belirsiz
❌ Risk değerlendirmesi: Düşen parça senaryosu değerlendirilmemiş
❌ Çalışan eğitimi: Anormal ses/titreşim durumunda işlem durdurma eğitimi eksik
⚠️ Kapı kullanım sıklığı yüksek - aşınma riski artar

3.4 İnsan Faktörü:
✅ Çalışan olay sonrası güvenli mesafeye çekildi
❌ Anormal ses fark edildi ama işlem durdurulmadı (tehlike algısı eksik)
❌ "Ses = Tehlike" refleksi gelişmemiş
⚠️ 2 metre mesafe - şans faktörü kritik rol oynadı

4. HASAR/SONUÇ
--------------
- Kişisel yaralanma: YOK ✅ (sadece 2 metre mesafe farkıyla)
- Ekipman hasarı: Sarmal kapı üst mekanizması hasarlı, kopan metal parça
- Malzeme hasarı: Test sahası zemin/çevre ekipmanlarında hafif hasar
- Potansiyel risk: ÇOK YÜKSEK (baş/omuz bölgesine düşme = ölüm/ciddi yaralanma)
- İş durumu: Kapı kullanım dışı, alternatif giriş/çıkış kullanılıyor

5. RAMAK KALA DEĞERLENDİRMESİ
-----------------------------
POTANSİYEL CİDDİ SONUÇLAR:
⚠️ Ölüm: Parça baş bölgesine düşseydi kafatası kırığı/iç kanama/ölüm
⚠️ Kalıcı sakatlık: Omur/omuz bölgesine düşme = omurga hasarı/felç
⚠️ Ağır yaralanma: İç kanama, kırıklar, uzun süreli iş göremezlik
⚠️ Psikolojik travma: Çalışan ve tanıklar üzerinde travmatik etki

NEDEN RAMAK KALA?
✅ Parça 2 metre uzağa düştü (şans faktörü)
✅ Çalışan o an kapı tam altında değildi
✅ Parça düşüş yörüngesi çalışandan uzakta

6. EK BİLGİLER
--------------
✅ Fotoğraflar: Mevcut (kopan parça, hasarlı mekanizma, düşme noktası)
✅ Tanık ifadeleri: Vardiya arkadaşları tanık (2 kişi) - anormal ses duyulduğunu doğruladılar
❌ Medikal rapor: Gerekmedi (yaralanma yok)
Diğer: 
- Kopan parça emniyet ekibi tarafından inceleme için ayrıldı
- Sarmal kapı acil bakım için kapatıldı
- Alternatif giriş/çıkış kapısı devreye alındı
- Tüm sarmal kapılar periyodik kontrole alındı
"""

    incident_data = {
        "ref_no": "02-26",
        "report_date": "21.01.2026",
        "incident_date": "20.01.2026",
        "incident_time": "09:10",
        "incident_type": "Ramak Kala (Near Miss)",
        "location": "MPT Test Sahası",
        "activity": "Test - Sarmal Kapı Kapatma İşlemi",
        "reported_by": "Hakan Sevil (Bölge Sorumlusu)",
        "description": incident_summary,
        "injury_description": "Kişisel yaralanma yok. Sarmal kapı üst mekanizmasından kopan metal parça çalışanın 2 metre yakınına düştü. Potansiyel ölüm/ciddi yaralanma riski (ramak kala).",
        "potential_severity": "ÇOK YÜKSEK (baş/omur bölgesine düşme = ölüm/kalıcı sakatlık riski)",
        "witnesses": ["Vardiya arkadaşı 1 (anormal ses duydu)", "Vardiya arkadaşı 2 (düşme anını gördü)"],
        "photos_available": True,
        "investigation_level": "Seviye A (Yüksek)"
    }

    print("\n" + "="*100)
    print("📋 ADIM 1: OVERVIEW AGENT - DÜŞEN PARÇA RAMAK KALA OLAYINI ANALİZ ET")
    print("="*100 + "\n")

    overview_agent = OverviewAgent()

    try:
        overview_result = overview_agent.process_initial_report(incident_data)

        print("\n✅ Overview Analizi Tamamlandı!")
        print(f"📊 Olay Tipi: {overview_result.get('incident_type', 'N/A')}")
        print(f"🏷️ Referans No: {overview_result.get('ref_no', 'N/A')}")
        print(f"⚠️ Ciddiyet: Ramak Kala (Potansiyel Ölüm/Ciddi Yaralanma Riski)")

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
        print(f"⚠️ Ramak Kala Değerlendirmesi: Potansiyel ölüm/kalıcı sakatlık riski")

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
        # ── META ROOT CAUSE ÖZELLİĞİ AKTİF ──
        root_cause_result = rootcause_agent.analyze_root_causes(
            overview_result,
            assessment_result,
            incident_data,
            synthesize_meta_root=True  # ← Birden fazla kök neden varsa meta analiz yap
        )

        print("\n✅ Kök Neden Analizi Tamamlandı!")

        branches = root_cause_result.get('analysis_branches', [])
        root_causes = root_cause_result.get('final_root_causes', [])
        meta_root = root_cause_result.get('meta_root_cause')

        print(f"\n🌳 Toplam {len(branches)} Ana Dal Tespit Edildi")
        print(f"🎯 Toplam {len(root_causes)} Kök Neden Bulundu")

        if meta_root:
            print("\n" + "="*100)
            print("🔗 META KÖK NEDEN (Tüm Dalların Ortak Paydası)")
            print("="*100)
            print(f"[{meta_root.get('code', '?')}] {meta_root.get('standard_title_tr', '')}")
            print(f"Açıklama: {meta_root.get('cause_tr', '')}")
            if meta_root.get('explanation_tr'):
                print(f"Neden: {meta_root.get('explanation_tr', '')}")
            synthesized = meta_root.get('synthesized_from_codes', [])
            if synthesized:
                print(f"Sentezlenen kodlar: {', '.join(synthesized)}")

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
        output_dir = Path("outputs/mpt_falling_part_near_miss")
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
            output_path = f"outputs/mpt_falling_part_near_miss/falling_part_report_{timestamp}.docx"

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
    print("✅ MPT DÜŞEN PARÇA RAMAK KALA SENARYOSU TESTİ TAMAMLANDI!")
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
            "source": "mpt_falling_part_near_miss",
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
                "source": "mpt_falling_part_near_miss",
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
