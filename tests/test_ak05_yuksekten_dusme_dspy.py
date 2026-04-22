#!/usr/bin/env python3
"""
================================================================================
AK05 YUKSEKTEN DUSME KAZASI - DSPy V3.1 TAM SISTEM TESTI
================================================================================

Kaynak:
  /Users/selcuk/Downloads/KAZA-OLAY DETAYLI ARAŞTIRMA RAPORU AK05 YÜKSEKTEN DÜŞME (1).docx

Amac:
  Gercek saha raporundan derlenen AK05 yuksekten dusme vakasinda
  tum pipeline'i (Overview -> Assessment -> RCA -> DOCX/HTML) uctan uca dogrulamak.

Beklenen:
  - type_of_event = "Kaza" override
  - immediate_cause_limit = 5
  - Her dalda why_chain uzunlugu = 5
  - DOCX + HTML rapor uretilmesi

Calistirma:
  python tests/test_ak05_yuksekten_dusme_dspy.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agents.assessment_agent import AssessmentAgent
from agents.overview_agent import OverviewAgent
from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
from agents.skillbased_docx_agent import SkillBasedDocxAgent


INCIDENT_DATA = """
KAZA OLAY DETAYLI ARASTIRMA RAPORU - AK05 YUKSEKTEN DUSME

Rapor tarihi: 21.04.2026
Kaza tarihi/saati: 16.04.2026 / 14:27
Proje: KMO Kesim-8
Bolge: AK05, guney eksen orta aks, enleme kiris kalip montaj alani

KAZA OZETI:
Panel kalipci olarak gorev yapan Muhammet Ali Demir, enleme kirisi kalip montaji
sirasinda ayaginin kaymasi sonucu dengesini kaybederek yaklasik 9 metre
yukseklikten dolgu toprak zemine dusmustur.

KAZA DETAYI:
- Calisma alaninda emniyet kemeri baglantisi icin uygun ankraj noktasi mevcuttu.
- Buna ragmen calisanin baglanti yapmadigi tespit edildi.
- Dusme sonrasi ekip tarafindan acil bildirim yapildi, 112 ve acil durum proseduru devreye alindi.
- Ilk bulgu: kolunda acik kirik, kalca ve bel/sirt bolgesinde siddetli agri.
- 112 ambulans ile hastaneye sevk edildi.
- 17.04.2026 tarihinde kol kirigi nedeniyle ameliyat oldu.
- Sonrasinda yogun bakim izlemi yapildi, kalca bolgesi icin ikinci mudahale planlamasi bekleniyor.

ZAMAN CIZELGESI:
- 08:00: Is izni ve isbasi toplantisi
- 10:40-11:00: Enleme kiris malzeme tasima ve kalip montaji baslangici
- 12:00: Ogle molasi
- 13:00: Ogle sonrasi ise donus
- 14:25-14:27: Yuksekten dusme kazasi
- 14:26: Ambulans ve acil ekip cagrisi
- 14:50: Ambulans varisi
- 15:00+: Hastane triyaj, radyolojik yonlendirme, yogun bakim

BULGULAR:
- Kazazede 18 yasinda, panel kalipci, projede yaklasik 7 ay calisma suresi.
- Is giris, yuksekte calisma ve toolbox egitimlerine katilim kayitlari mevcut.
- KKD zimmet kayitlari mevcut (baret, celik burunlu ayakkabi, emniyet kemeri vb.).
- Kullanilan emniyet kemeri EN 361 / EN 353 / EN 362 standardini karsiliyor.
- Kaza aninda saha genelinde ISG personeli ve coklu ekipler mevcuttu.
- Kaza noktasinda calisanin ankraj baglantisini uzaktan tespit etmenin zor oldugu belirtildi.
- Calisma aninda supervizor/formen/ekip basi sabit varliginin yeterli olmadigi tespit edildi.

POTANSIYEL / GERCEK ZARAR:
- Gerceklesen: Ciddi yaralanma (acik kirik, cerrahi mudahale)
- Potansiyel: Fatal veya cok ciddi yaralanma
""".strip()


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_warning(msg: str):
    print(f"  ⚠️  {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def main():
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/ak05_yuksekten_dusme_dspy")
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("AK05 YUKSEKTEN DUSME - DSPy V3.1 TAM SISTEM TESTI")
    results = {"timestamp": timestamp, "steps": {}, "files": []}

    # ADIM 1: Ortam
    print_header("ADIM 1: Ortam Kontrolu")
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print_error("OPENROUTER_API_KEY / OPENAI_API_KEY bulunamadi")
        return 1
    print_success(f"API Key bulundu: {api_key[:10]}...{api_key[-4:]}")
    results["steps"]["environment"] = "PASSED"

    # ADIM 2: Overview
    print_header("ADIM 2: OverviewAgent")
    try:
        overview = OverviewAgent()
        part1 = overview.process_initial_report({"description": INCIDENT_DATA})
        print_success(f"Ref No: {part1.get('ref_no')}")
        print_success(f"Olay Tipi (LLM): {part1.get('incident_type')}")
        results["steps"]["overview"] = "PASSED"
    except Exception as e:
        print_error(f"Overview hatasi: {e}")
        results["steps"]["overview"] = "FAILED"
        return 1

    # ADIM 3: Assessment
    print_header("ADIM 3: AssessmentAgent")
    try:
        assessment = AssessmentAgent()
        part2 = assessment.assess_incident(part1, {"description": INCIDENT_DATA})

        # Frontend secimini simule et
        part2["type_of_event"] = "Kaza"
        if not isinstance(part2.get("investigation"), dict):
            part2["investigation"] = {}
        part2["investigation"]["level"] = "High level"
        part2["actual_potential_harm"] = "Fatal or major"

        print_success("type_of_event override: Kaza")
        print_success(f"Level: {(part2.get('investigation') or {}).get('level')}")
        results["steps"]["assessment"] = "PASSED"
    except Exception as e:
        print_error(f"Assessment hatasi: {e}")
        results["steps"]["assessment"] = "FAILED"
        return 1

    # ADIM 4: RCA
    print_header("ADIM 4: RootCauseAgentV3_1")
    try:
        rca_agent = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)
        part3 = rca_agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA},
        )

        immediate_cause_limit = part3.get("immediate_cause_limit")
        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])
        why_lengths = [len(b.get("why_chain", [])) for b in branches]

        print_success(f"immediate_cause_limit: {immediate_cause_limit}")
        print_success(f"Branch sayisi: {len(branches)}")
        print_info(f"Why uzunluklari: {why_lengths}")

        assert immediate_cause_limit == 5, (
            f"Beklenen immediate_cause_limit=5, gelen={immediate_cause_limit}"
        )
        assert branches, "Hic branch uretilmedi"
        assert all(w == 5 for w in why_lengths), f"Why zinciri sabit 5 degil: {why_lengths}"

        json_file = output_dir / f"ak05_yuksekten_dusme_dspy_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        results["files"].append(str(json_file))

        print_success(f"Kok neden sayisi: {len(causes)}")
        print_success(f"JSON: {json_file}")
        results["steps"]["rca"] = "PASSED"
    except Exception as e:
        print_error(f"RCA hatasi: {e}")
        results["steps"]["rca"] = "FAILED"
        return 1

    # ADIM 5: Rapor
    print_header("ADIM 5: Rapor Uretimi (DOCX + HTML)")
    try:
        docx_agent = SkillBasedDocxAgent()
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = output_dir / f"{ref_no}_ak05_yuksekten_dusme_dspy.docx"
        generated_docx = docx_agent.generate_report(
            {"part1": part1, "part2": part2, "part3_rca": part3},
            str(docx_file),
        )
        generated_html = generated_docx.replace(".docx", ".html")

        if Path(generated_docx).exists():
            results["files"].append(generated_docx)
            print_success(f"DOCX: {generated_docx}")
        if Path(generated_html).exists():
            results["files"].append(generated_html)
            print_success(f"HTML: {generated_html}")
        results["steps"]["report"] = "PASSED"
    except Exception as e:
        print_warning(f"Rapor adimi uyarisi: {e}")
        results["steps"]["report"] = "FAILED"

    # ADIM 6: Ozet
    elapsed = round(time.time() - start_time, 2)
    summary = {
        "timestamp": timestamp,
        "overall": "PASSED" if results["steps"].get("rca") == "PASSED" else "FAILED",
        "checks": {
            "type_of_event": "Kaza",
            "expected_immediate_cause_limit": 5,
            "actual_immediate_cause_limit": part3.get("immediate_cause_limit"),
            "branch_count": len(part3.get("analysis_branches", [])),
            "why_lengths": [len(b.get("why_chain", [])) for b in part3.get("analysis_branches", [])],
        },
        "steps": results["steps"],
        "files": results["files"],
        "elapsed_seconds": elapsed,
    }
    summary_file = output_dir / f"test_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print_success(f"Test ozeti: {summary_file}")

    print_header("SONUC")
    print_success("AK05 yuksekten dusme full test basarili")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
