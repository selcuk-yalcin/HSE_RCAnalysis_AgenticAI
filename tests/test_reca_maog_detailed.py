"""
KOK NEDEN ANALIZI TESTI - RECA MAOG Kazi Gocugu Olayi
=========================================================

TEST AKISI (Sadece Kok Neden - Rapor YOK):
1. Overview Agent      -> Olayi analiz et, baglami olustur
2. Assessment Agent    -> Risk degerlendir, kronoloji cikar
3. RootCause Agent V2  -> 3 dal hiyerarsik analiz (5-Why)

NOT: DOCX/HTML rapor uretimi YAPILMAZ, sadece kok neden analizi cikarilir.
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


def main():
    print("=" * 80)
    print("KOK NEDEN ANALIZI TESTI - RECA MAOG Kazi Gocugu Senaryosu")
    print("   (Sadece Part 1-3, rapor uretimi YOK)")
    print("=" * 80)
    print()

    incident_summary = (
        "KAZA SORUSTURMA RAPORU -- KAZI GOCUGU (LTI)\n"
        "Rapor No: RECA-MAOG-IRP-26-00765\n"
        "Tarih: 12 Subat 2026\n"
        "\n"
        "1. ON BILGILER\n"
        "Olay Turu: Kayip Is Gunlu Kaza (LTI) -- Kazi Gocugu\n"
        "Lokasyon: MAOG Projesi, Mersin-Adana Kesimi KM 359+300\n"
        "Tarih/Saat: 12.02.2026 / 16:15\n"
        "Kazazede: Nuri Karakus, Erkek, 50 yas (d. 15.11.1976)\n"
        "Egitim Durumu: Ilkokul\n"
        "Pozisyon: Plastik Kaynakcisi\n"
        "Isveren: Akdeniz Altyapi (alt yuklenici)\n"
        "Kidem: Pozisyonda 2 yil 10 ay 12 gun; firmada ~10 yil (ilk SGK girisi 07.09.2016)\n"
        "\n"
        "2. OZET\n"
        "12.02.2026 tarihinde saat 16:15 sularinda, KM 359+300 mevkiinde Akdeniz Altyapi "
        "tarafindan yurutulen atik-su hatti deplase calismalarinda, kazi alaninda boru montaji "
        "yapan Nuri Karakus kazi yuzeyindeki ani toprak kaymasi sonucu gocuk altinda kaldi. "
        "Ayni ekipte calisan Ibrahim Karademir kazi yuzeyindeki hareketliligi fark ederek "
        "calisani uyardi; ancak cikis esnasinda gocuk gerceklesti. Kazazede ekip tarafindan "
        "~5 dk'da kurtarildi, 112 Acil ve REC Acil Cagri arandi; saat 16:40'ta olay yerine "
        "ulasan ambulansla bilinci acik sekilde Adana Sehir Hastanesi'ne sevk edildi.\n"
        "\n"
        "3. KAZANIN DETAYLI ACIKLAMASI\n"
        "- 08:00 - TRIC kart egitimi (konu: Demir tezgah calismalari -- kazi faaliyetiyle uyumsuz).\n"
        "- 08:30-11:40 - 600 mm capli 8 adet beton boru montaji + dolgu; ogle molasi.\n"
        "- 13:15-15:15 - 3 boru daha montajlandi (toplam 11). Dolgu bitti, 14:30'da yagmur baslayip siddetlendi; ekip beklemeye gecti.\n"
        "- 15:15 - Alt isveren santiye sefi Niyazi Tanriverdi sahaya geldi; yagis nedeniyle calisma sonlandirildi.\n"
        "- 15:30 - REC OSGB ISG denetcisi Harun Bedircan sahaya geldi, karar teyit edildi; her ikisi sahadan ayrildi.\n"
        "- ~16:10 - Calisanlar, 3. sahsa ait sundurma ayaginin kazi kenarinda bosaldigini ve cokme riski olustugunu degerlendirerek 12. borunun montajini tamamlamaya karar verdi (yetkisiz yeniden baslatma).\n"
        "- 16:15 - Nuri Karakus kazi icinde zemin duzenleme yaparken kuzey yuzeyinde catlak olustu; ekip uyardi; kacamadan gocuk meydana geldi.\n"
        "- 16:15-16:20 - Ekip ve cevredekiler tarafindan gocuk altindan kurtarildi; 112 cagrildi; ilk yardim uygulandi.\n"
        "- 16:40 - Ambulansla Adana Sehir Hastanesi'ne sevk.\n"
        "\n"
        "4. ZAMAN CIZELGESI\n"
        "| Saat | Lokasyon | Olay | Faz |\n"
        "|---|---|---|---|\n"
        "| 08:00-08:30 | KM 359+300 | TRIC Kart egitimi (Demir tezgah) | Kaza oncesi |\n"
        "| 08:30-10:00 | KM 359+300 | 5 adet 600 mm boru montaji | Kaza oncesi |\n"
        "| 10:00-10:15 | KM 359+300 | Cay molasi | Kaza oncesi |\n"
        "| 10:15-11:40 | KM 359+300 | 3 adet boru montaji | Kaza oncesi |\n"
        "| 11:40-13:15 | KM 359+300 | Ogle molasi | Kaza oncesi |\n"
        "| 13:15-15:15 | KM 359+300 | 3 boru montaji; yagmur + dolgu yok -> bekleme | Kaza oncesi |\n"
        "| 15:15-15:30 | KM 359+300 | Santiye sefi + ISG denetcisi: calisma sonlandirildi bildirimi | Kaza oncesi |\n"
        "| 16:10-16:15 | KM 359+300 | Sundurma cokme riski -> yetkisiz calisma karari | Kaza oncesi |\n"
        "| 16:15 | KM 359+300 | Gocuk -- Nuri Karakus toprak altinda kaldi | Kaza ani |\n"
        "| 16:15-16:20 | KM 359+300 | Kurtarma + 112 cagrisi | Kaza sonrasi |\n"
        "| 16:40-17:00 | Adana Sehir Hast. | Ambulansla sevk; bilinc acik | Kaza sonrasi |\n"
        "\n"
        "5. BULGULAR VE DETAYLAR\n"
        "\n"
        "5.1 Personel Hakkinda\n"
        "- SGK meslegi: 7212.36 - Plastik Kaynakci. MYK belgesi: 09UY0001-3/02 (Seviye 3, gecerli 24.07.2027).\n"
        "- Saglik muayenesi 01.09.2025 -- calismasina engel yok.\n"
        "- ISG egitimleri: 16 saat temel ISG (01-02.09.2025); oryantasyon + kazi tehlikeleri (03.09.2025); 463 toolbox (35'i kazi), 82 interaktif (20'si kazi).\n"
        "- TCDD 551 egitimi 29.03.2025'te suresi dolmus.\n"
        "- Son TRIC kart egitimleri: 10-11-12 Subat 2026.\n"
        "- Disiplin kaydi: Yok.\n"
        "- Gocuk tatbikati: 12.06.2024'te senaryo bazli tatbikat yapilmis; ancak teorik bilgi sahada davranisa donusmemis.\n"
        "\n"
        "5.2 Gorusme Yapilan Kisiler\n"
        "Nuri Karakus (kazazede - henuz gorusulemedi), Adem Toslak (ekskavator op.), Gurkan Demir (uygulama sor.), "
        "Niyazi Tanriverdi (santiye sefi), Burak Kekevi (REC Deplase kisim sefi), Serdar Tumtas (REC tekniker), "
        "Omer Dundar & Ali Kaan Benli (Akdeniz ISG uzmanlari), Harun Bedircan (Hekimbey ISG uzmani).\n"
        "\n"
        "5.3 Cevre ve Kaza Yeri\n"
        "- Hava: 13-15 C; son 24 saatte 94.0 mm yagis (Subat ortalamasinin %115'i -> major cevresel degisim).\n"
        "- Zemin: Suya tamamen doygun; tasima kapasitesi ve kayma direnci yok.\n"
        "- Kazi: Genislik 1,40 m; derinlik 2,60 m; kanal kazisi. Sev UYGULANMADI, iksa UYGULANMADI -- prosedur ihlali.\n"
        "- Zemin turu kaza oncesinde DEGERLENDIRILMEDI (kaza sonrasi 'A tipi' olarak raporlandi).\n"
        "- Is izni: 198 (kazi) & 655 (deplase), 10-16 Subat gecerli; 94 mm yagis sonrasi otomatik iptal EDILMEDI.\n"
        "- 3. sahsa ait sundurma yapinin tasiyici ayagi kazi kenarinda; alt kismi bosalmisti.\n"
        "- Kazi tehlikeleri isaret levhasi YOKTU.\n"
        "\n"
        "5.4 Risk Yonetim Araclari ve Prosedurler\n"
        "- Yapim Yontemi (AKD-MA-ALT-DPL-076): Madde 6.7 'Siddetli yagmurda calisma yapilmaz' -> IHLAL. >=1,50 m kazida sev/iksa -> IHLAL.\n"
        "- Akdeniz RA maddeleri (441, 458, 469, 478, 479, 526, 547) ve REC RA maddeleri (1102, 1159) kazi sevi/iksa kontrolunu tanimlar; sahada uygulanmadi.\n"
        "- ITA (AKD 010): Sev/iksa ile guvenlik saglanacak denilmis; sahada UYGULANMADI.\n"
        "- Kazi Prosedürleri (HOL-HSE-PRO-108 & MAOG-PRG-0018):\n"
        "  - 7.4.1.1: Cokme riski varsa derinlik fark etmez, destekleme yapilir.\n"
        "  - 7.4.1.2: >1,2 m'de sev/iksa olmadan ASLA calisilmaz.\n"
        "  - 7.12: Yagista kazi calismasi YAPILMAZ; yagis sonrasi Toprak Isleri Sefi kontrol eder.\n"
        "- Prosedur uyum oranlari: Q3-2025 %82, Q4-2025 %78 -> sev/iksa sapmalarinda sistematik zafiyet.\n"
        "- Is Izni Sistemi (PTW): Yetki rolleri birlestirilmis; 94 mm yagis sonrasi PTW otomatik iptal edilmedi; REC ISG 'GORULDU' kasesi kullanilmadi.\n"
        "- TRIC Kart: Kaza gunu konusu 'Demir tezgah' -- kazi faaliyetiyle UYUMSUZ. Yagis sonrasi TRIC guncellenmedi.\n"
        "- TBT (Toolbox Talk) yapilmadi -- gocuk riski aktarilmadi.\n"
        "\n"
        "5.5 Organizasyon\n"
        "- Akdeniz Altyapi: 198 personel; 7/24-tek vardiya; 2 C-sinifi ISG uzmani. Kaza gunu bolge ISG sorumlusu saglik problemi nedeniyle YOKTU.\n"
        "- REC Denetimi: 7 aktif lokasyona 1 sef + 2 tekniker. Kaza gunu deplase sefi saatlik izinde, vekil belirlenmedi; Serdar Tumtas kontrolden sorumlu -> kapasite yetersiz.\n"
        "- 2025-2026: 777 uygunsuzluk, 54 is durdurma, 32 disiplin (25 uyari, 5 kinama, 2 agir kinama); Santiye Sefi hakkinda 3 disiplin kaydi; 566.300 TL idari ceza.\n"
        "- 2025'te 22 toplanti; koordinasyon, kurul, risk calistayi yapilmis.\n"
        "\n"
        "Acil Onlemler: Gocukten kurtarma (~5 dk), 112 arandi, REC Acil bilgilendirildi, ilk yardim, ambulansla sevk, alan guvenlige alindi, sorusturma baslatildi.\n"
        "\n"
        "Temel Bulgular:\n"
        "1. Kaza onlenebilirdi -- erken sinyaller mevcuttu (777 uygunsuzluk, onceki ramak kalalar).\n"
        "2. Prosedurler yazilmisti (kazi guvenligi, yagista calisma yasagi, otomatik PTW iptali >=50 mm).\n"
        "3. Coklu bariyer ihlali: teknik, prosedürel, gozetim ve davranissal.\n"
        "4. Major cevresel degisim (94 mm) yonetilemedi.\n"
        "5. Dinamik risk zinciri (TRIC -> TBT -> PTW) islemedi.\n"
        "6. Yetkisiz calisma yeniden baslatildi (is durdurma karari sonrasi)."
    )

    incident_data = {
        "incident_summary": incident_summary,
        "description": incident_summary,
        "injury_description": "Gocuk altinda kalma sonucu yaralanma - LTI (Lost Time Injury). Kazazede bilinci acik sekilde hastaneye sevk edilmistir.",
    }

    print("=" * 80)
    print("RECA MAOG KAZA BILGILERI")
    print("=" * 80)
    print(f"   Ozet uzunlugu: {len(incident_summary)} karakter")
    print()

    # AGENT'LARI BASLAT
    print("=" * 80)
    print("AGENT'LAR BASLATILIYOR (Sadece Part 1-3)...")
    print("=" * 80)
    print()

    overview_agent = OverviewAgent()
    assessment_agent = AssessmentAgent()
    rootcause_agent = RootCauseAgent()

    print("\nTum ajanlar baslatildi (rapor ajani haric)")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("KOK NEDEN ANALIZI BASLIYOR (3 ADIM)")
    print("   1. Overview Agent: Genel bakis ve baglam analizi")
    print("   2. Assessment Agent: Risk degerlendirme ve kronoloji")
    print("   3. RootCause Agent V2: 3-dal hiyerarsik kok neden (5-Why)")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("ANALIZ BASLIYOR")
    print("=" * 80)

    results = {
        "part1": None,
        "part2": None,
        "part3_rca": None,
        "status": "initialized",
    }

    try:
        print("\nADIM 1/3: Genel Bakis (Part 1)")
        print("-" * 80)
        results["part1"] = overview_agent.process_initial_report(incident_data)
        results["status"] = "part1_complete"

        print("\nADIM 2/3: Degerlendirme (Part 2)")
        print("-" * 80)
        results["part2"] = assessment_agent.assess_incident(
            results["part1"], incident_data
        )
        results["status"] = "part2_complete"

        print("\nADIM 3/3: Kok Neden Analizi (Part 3)")
        print("-" * 80)
        results["part3_rca"] = rootcause_agent.analyze_root_causes(
            results["part1"],
            results["part2"],
            incident_data.get("investigation_details"),
        )
        results["status"] = "analysis_complete"

    except Exception as e:
        print(f"\nAnaliz hatasi: {e}")
        results["status"] = "error"
        results["error"] = str(e)
        raise

    # SONUC OZETI
    print("\n" + "=" * 80)
    print("KOK NEDEN ANALIZI TAMAMLANDI")
    print("=" * 80)

    p1 = results.get("part1", {})
    p2 = results.get("part2", {})
    p3 = results.get("part3_rca", {})

    print(f"\nReferans No:       {p1.get('ref_no', 'N/A')}")
    print(f"Olay Tipi:         {p1.get('incident_type', 'N/A')}")
    print(f"Siddet:            {p2.get('actual_potential_harm', 'N/A')}")
    print(f"Sorusturma Duzeyi: {p2.get('investigation_level', 'N/A')}")
    print(f"RIDDOR:            {p2.get('riddor_reportable', 'N/A')}")

    branches = p3.get("analysis_branches", [])
    root_causes = p3.get("final_root_causes", [])
    print(f"\nAnaliz Dali Sayisi: {len(branches)}")
    print(f"Kok Neden Sayisi:   {len(root_causes)}")

    # KOK NEDENLER
    if root_causes:
        print("\n" + "=" * 80)
        print("BULUNAN KOK NEDENLER")
        print("=" * 80)
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("code", "N/A")
            name = rc.get("name", "N/A")
            desc = rc.get("description", "N/A")
            print(f"\n  {i}. [{code}] {name}")
            print(f"     {desc}")

    if branches:
        print("\n" + "=" * 80)
        print("DAL OZETLERI")
        print("=" * 80)
        for i, branch in enumerate(branches, 1):
            dc = branch.get("direct_cause", {})
            rc = branch.get("root_cause", {})
            chain = branch.get("five_why_chain", [])
            dc_code = dc.get("code", "?")
            dc_desc = dc.get("description", "N/A")[:80]
            rc_code = rc.get("code", "?")
            rc_desc = rc.get("description", "N/A")[:80]
            print(f"\n  Dal {i}: [{dc_code}] {dc_desc}...")
            print(f"         -> {len(chain)} Why ->")
            print(f"         [{rc_code}] {rc_desc}...")

    # JSON KAYDET
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_output = output_dir / f"reca_maog_rootcause_{timestamp}.json"

    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    json_size_kb = os.path.getsize(json_output) / 1024
    print(f"\nJSON Sonuclar: {json_output} ({json_size_kb:.1f} KB)")

    # BASARI KRITERLERI KONTROLU
    print("\n" + "=" * 80)
    print("BASARI KRITERLERI KONTROLU")
    print("=" * 80)
    print()

    checks = {
        "Part 1 tamamlandi": results.get("part1") is not None,
        "Part 2 tamamlandi": results.get("part2") is not None,
        "Part 3 RCA tamamlandi": results.get("part3_rca") is not None,
        "3 analiz dali var": len(branches) >= 3,
        "Kok nedenler var (>=2)": len(root_causes) >= 2,
        "JSON kaydedildi": os.path.exists(json_output),
        "Final durum 'complete'": results["status"] == "analysis_complete",
    }

    passed = sum(checks.values())
    total = len(checks)

    for check, result in checks.items():
        symbol = "PASS" if result else "FAIL"
        print(f"[{symbol}] {check}")

    print(f"\nSkor: {passed}/{total} ({100*passed//total}%)")
    print()

    if passed == total:
        print("TUM TESTLER BASARILI! Kok neden analizi tam olarak calisiyor.")
    else:
        print("Bazi kontroller basarisiz oldu. Lutfen yukardaki detaylari inceleyin.")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
