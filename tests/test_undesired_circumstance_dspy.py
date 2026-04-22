#!/usr/bin/env python3
"""
================================================================================
GUVENSIZ DURUM OLAYI - DSPy V3.1 TAM SISTEM TESTI
================================================================================

Amac:
  test_electrical_shock_dspy.py akisina benzer sekilde tum pipeline'i calistirip,
  type_of_event = "Guvensiz Durum" icin immediate_cause_limit = 3 davranisini
  dogrulamak.

Beklenen:
  - immediate_cause_limit = 3
  - Her dalda why_chain uzunlugu = 5
  - DOCX + HTML rapor uretilir

Calistirma:
  python tests/test_undesired_circumstance_dspy.py
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
OLAY RAPORU - GUVENSIZ DURUM (UNDESIRED CIRCUMSTANCE)

Tarih: 24 Nisan 2026, Saat: 11:20
Lokasyon: Pres Hatti - Sac Besleme Bolgesi
Rapor Eden: Hat Sorumlusu

OLAY ACIKLAMASI:
Pres hattinda koruyucu isigik perdesi devreye girmeden makine hareketi gozlemlendi.
Calisan eli tehlikeli bolgeye yakin olmasina ragmen yaralanma olmadi.

KRONOLOJI:
- 11:10 - Hatta sensor hatasi ikazi goruldu
- 11:20 - Isik perdesi aktif degilken pres stroku aldi
- 11:21 - Acil durdurma ile hat durduruldu
- 11:28 - Bakim ekibi alana cagriildi

ETKI:
- Yaralanma: Yok
- Potansiyel: Ciddi ezilme / amputasyon riski
- Maddi hasar: Yok

ON BULGULAR:
- Isik perdesi bypass edilmis olabilir
- Vardiya baskisi nedeniyle ariza ile calismaya devam edilmis
- Gecici cozumler kalici hale gelmis
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
    output_dir = Path("outputs/undesired_circumstance_dspy")
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("GUVENSIZ DURUM - DSPy V3.1 TAM SISTEM TESTI")
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
        print_success(f"Olay Tipi: {part1.get('incident_type')}")
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
        part2["type_of_event"] = "Guvensiz Durum"
        if not isinstance(part2.get("investigation"), dict):
            part2["investigation"] = {}
        part2["investigation"]["level"] = "Medium level"
        part2["actual_potential_harm"] = "Serious injury potential"

        print_success("type_of_event override: Guvensiz Durum")
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

        assert immediate_cause_limit == 3, (
            f"Beklenen immediate_cause_limit=3, gelen={immediate_cause_limit}"
        )
        assert branches, "Hic branch uretilmedi"
        assert all(w == 5 for w in why_lengths), f"Why zinciri sabit 5 degil: {why_lengths}"

        json_file = output_dir / f"undesired_circumstance_dspy_{timestamp}.json"
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
        docx_file = output_dir / f"{ref_no}_undesired_circumstance_dspy.docx"
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
            "type_of_event": "Guvensiz Durum",
            "expected_immediate_cause_limit": 3,
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
    print_success("Guvensiz durum full test basarili")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
