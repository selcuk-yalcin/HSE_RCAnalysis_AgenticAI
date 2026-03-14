"""
SENARYO 2: YAĞ TASFİYE CİHAZI YANMASI - YANLIŞ DEVREYE ALMA SIRASI
=====================================================================
Farklılıklar:
- Ekipman hasarı (kişisel yaralanma değil)
- Yazılı iş talimatı eksikliği
- Uyarıcı/bilgilendirici levha eksikliği
- Emniyet sistemi/interlock eksikliği (diğer cihazlarda var, bu cihazda yok)
- Deneyimli çalışan (4 yıl kıdem, fazla mesai yok, oruçlu değil)
- Vardiya değişimi bağlamı
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


def main():
    print("=" * 100)
    print("🔥 YAĞ TASFİYE CİHAZI YANMASI SENARYOSU - YANLIŞ DEVREYE ALMA TESTİ")
    print("=" * 100)
    print()

    incident_summary = """
KAZA RAPORU - YAĞ TASFİYE CİHAZI YANMASI
==========================================

1. OLAY ÖZETİ
-------------
Saat 15:20'de görevli yağcı, yağ tasfiye cihazını "ON" konumuna alarak sistemi devreye
sokmuştur. Ancak normal çalışma sırasına göre cihaz devreye alınmadan önce hat vanasının
açılması gerekmekteyken, ilgili çalışan tarafından vana açılmadan cihaz çalıştırılmıştır.
Çalışan, cihazı devreye aldıktan sonra hat vanasını açmadan alandan ayrılmıştır.

Yaklaşık 15–20 dakika sonra vardiya değişimi gerçekleşmiş, ilk yağcı vardiyadan ayrılmış
ve yeni yağcı görev başı yapmıştır. Göreve başlayan yeni yağcı, yağ tasfiye cihazından
duman çıktığını fark etmiş ve durumu derhal ilgili kişilere bildirmiştir. Yapılan bildirim
üzerine cihaz kapatılmış ve güvenli müdahale amacıyla soğumaya bırakılmıştır. Olaydan
yaklaşık 12 saat sonra cihaz sökülerek iç kısmında detaylı inceleme yapılmış,
gerçekleştirilen kontrolde cihazın iç aksamında yanma meydana geldiği tespit edilmiştir.

2. ZAMAN ÇİZELGESİ
------------------
15:20       - Görevli yağcı, yağ tasfiye cihazını "ON" konumuna aldı (hat vanası açılmadan)
15:20       - Çalışan hat vanasını açmadan alandan ayrıldı
15:35~15:40 - Vardiya değişimi gerçekleşti (ilk yağcı vardiyadan ayrıldı)
15:35~15:40 - Yeni yağcı göreve başladı, cihazdan duman çıktığını fark etti
15:35~15:40 - Durum derhal ilgili kişilere bildirildi, cihaz kapatıldı
+12 saat    - Cihaz söküldü, iç kısım incelendi; iç aksamda yanma tespit edildi

3. BULGULAR
-----------

3.1 Personel:
✅ Deneyim: 4 yıllık kıdemli ve tecrübeli personel, işi bilen personel
✅ Aşırı fazla mesai: Son iki haftada YOK
✅ Oruç durumu: Olay sırasında oruçlu DEĞİL
❌ Yazılı çalışma talimatı: İlgili işin güvenli yürütülmesine yönelik yazılı talimat VERİLMEMİŞ

3.2 Ekipman/Sistem:
❌ Yağ akışı sağlanmadan ısıtmayı devre dışı bırakacak sensör: YOK (bu cihazda)
❌ İnterlock sistemi: YOK (bu cihazda)
✅ Tesisteki diğer iki benzer cihaz: Yağ akışı sağlanmadığında ısıtma işlemini başlatmayan
   emniyet sensörleri veya interlock sistemi VAR

3.3 Yönetim Sistemi:
❌ Yazılı iş talimatı: Güvenli devreye alma sırasına dair yazılı talimat YOK
❌ Uyarıcı/bilgilendirici levha: Cihazın doğru devreye alma sırası ve hatalı kullanım
   riskleriyle ilgili çalışma alanında levha YOK
   Teknik Risk Analizlerinin (HAZOP/LOPA) yapıldığı tespit edilmiştir.

4. HASAR/SONUÇ
--------------
- Kişisel yaralanma: YOK
- Ekipman hasarı: Yağ tasfiye cihazı iç aksamında yanma
"""

    incident_data = {
        "ref_no": "OIL-2026-002-FIRE",
        "reported_by": "Vardiya Amiri",
        "date_time": "15:20",
        "description": incident_summary,
        "injury_description": "Kişisel yaralanma yok. Yağ tasfiye cihazı iç aksamında yanma (ekipman hasarı)."
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
        print(f"📋 RIDDOR: {assessment_result.get('riddor_reportable', 'N/A')}")

    except Exception as e:
        print(f"❌ HATA (Assessment): {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "="*100)
    print("📋 ADIM 3: ROOT CAUSE AGENT V2 - KÖK NEDEN ANALİZİ (5-WHY)")
    print("="*100 + "\n")

    rootcause_agent = RootCauseAgentV2(use_rag=True)  # ← RAG KAPALI

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
        output_dir = Path("outputs/oil_purifier_fire_test")
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
            output_path = f"outputs/oil_purifier_fire_test/oil_purifier_fire_report_{timestamp}.docx"

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
    print("✅ YAĞ TASFİYE CİHAZI YANMASI SENARYOSU TESTİ TAMAMLANDI!")
    print("  📊 JSON raporlar oluşturuldu")
    print("  📄 HTML tam rapor oluşturuldu")
    print("  📄 DOCX tam rapor oluşturuldu")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
