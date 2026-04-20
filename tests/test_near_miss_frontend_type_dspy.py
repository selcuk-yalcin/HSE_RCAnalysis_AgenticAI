#!/usr/bin/env python3
"""
================================================================================
RAMAK KALA OLAYI - FRONTEND TYPE OF EVENT ODAKLI DSPy V3.1 TESTİ
================================================================================

Amaç:
  test_electrical_shock_dspy.py akışına benzer tam pipeline çalıştırıp,
  frontend seçiminden gelen "type_of_event" alanının dal sayısını düşürdüğünü
  doğrulamak.

Beklenen:
  - part2["type_of_event"] = "Ramak Kala Olay"
  - RCA çıktısında immediate_cause_limit = 2
  - Her dalda why_chain uzunluğu sabit 5

Çalıştırma:
  python tests/test_near_miss_frontend_type_dspy.py
"""
  
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
from agents.skillbased_docx_agent import SkillBasedDocxAgent


INCIDENT_DATA = """
OLAY RAPORU - RAMAK KALA (DÜŞEN PARÇA)

Tarih: 22 Mart 2026, Saat: 10:15
Lokasyon: Paketleme Hattı - Sarmal Kapı Girişi
Rapor Eden: Vardiya Amiri - Deniz Aktaş

OLAY AÇIKLAMASI:
Sarmal kapının üst mekanizmasından metal bağlantı parçası koparak yere düştü.
Parça, çalışan Ahmet K.'nin yaklaşık 1 metre yanına düştü, yaralanma olmadı.
Çalışanlar bölgede anormal sürtünme sesi duyduklarını ancak hattı durdurmadıklarını belirtti.

OLAY KRONOLOJİSİ:
- 09:50 - Kapıdan geçişlerde anormal ses başladı
- 10:05 - Operatör sesin arttığını bildirdi
- 10:15 - Metal parça koparak zemine düştü
- 10:16 - Bölge emniyete alındı, kapı devre dışı bırakıldı
- 10:25 - Bakım ekibi ilk incelemeyi yaptı

ETKİ:
- Yaralanma: Yok
- Maddi hasar: Kapı mekanizmasında hasar
- Potansiyel risk: Baş-boyun travması riski
""".strip()


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_ok(msg: str):
    print(f"  ✅ {msg}")


def print_warn(msg: str):
    print(f"  ⚠️  {msg}")


def print_err(msg: str):
    print(f"  ❌ {msg}")


def main():
    start = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("outputs/near_miss_frontend_type_dspy")
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("RAMAK KALA - FRONTEND TYPE OF EVENT TESTİ")

    # ADIM 1 - ENV
    print_header("ADIM 1: Ortam Kontrolü")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print_err("OPENROUTER_API_KEY bulunamadı")
        return 1
    print_ok(f"API Key bulundu: {api_key[:8]}...{api_key[-4:]}")

    # ADIM 2 - OVERVIEW
    print_header("ADIM 2: OverviewAgent")
    try:
        overview = OverviewAgent()
        part1 = overview.process_initial_report({"description": INCIDENT_DATA})
        print_ok(f"Ref No: {part1.get('ref_no', 'N/A')}")
        print_ok(f"Incident Type (LLM): {part1.get('incident_type', 'N/A')}")
    except Exception as e:
        print_err(f"Overview hata: {e}")
        return 1

    # ADIM 3 - ASSESSMENT
    print_header("ADIM 3: AssessmentAgent")
    try:
        assessment = AssessmentAgent()
        part2 = assessment.assess_incident(part1, {"description": INCIDENT_DATA})
    except Exception as e:
        print_err(f"Assessment hata: {e}")
        return 1

    # Frontend seçimini simüle et: type_of_event = Ramak Kala Olay
    part2["type_of_event"] = "Ramak Kala Olay"
    print_ok("type_of_event frontend override: Ramak Kala Olay")
    print_ok(f"Severity: {part2.get('actual_potential_harm', 'N/A')}")
    print_ok(f"Investigation level: {(part2.get('investigation') or {}).get('level', 'N/A')}")

    # ADIM 4 - RCA V3.1
    print_header("ADIM 4: RootCauseAgentV3_1")
    try:
        rca = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)
        part3 = rca.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA},
        )
    except Exception as e:
        print_err(f"RCA hata: {e}")
        return 1

    immediate_cause_limit = part3.get("immediate_cause_limit")
    branches = part3.get("analysis_branches", [])
    why_lengths = [len(b.get("why_chain", [])) for b in branches]

    print_ok(f"Immediate cause limit: {immediate_cause_limit}")
    print_ok(f"Branch sayısı: {len(branches)}")
    print_ok(f"Why zincir uzunlukları: {why_lengths}")

    # Beklenti kontrolleri
    if immediate_cause_limit != 2:
        print_err(f"Beklenen immediate_cause_limit=2, gelen={immediate_cause_limit}")
        return 1
    if not branches:
        print_err("Hiç branch üretilmedi")
        return 1
    if any(length != 5 for length in why_lengths):
        print_err(f"Why zinciri sabit 5 değil: {why_lengths}")
        return 1
    if len(part3.get("final_root_causes", [])) > 2:
        print_err("Ramak kala için kök neden sayısı 2'yi aştı")
        return 1

    print_ok("RCA kuralları doğrulandı (limit=2, each why=5)")

    # ADIM 5 - RAPOR
    print_header("ADIM 5: Rapor Üretimi")
    try:
        docx_agent = SkillBasedDocxAgent()
        ref_no = part1.get("ref_no", f"INC-{timestamp}")
        docx_path = output_dir / f"{ref_no}_near_miss_frontend_type_dspy.docx"
        result_docx = docx_agent.generate_report(
            {"part1": part1, "part2": part2, "part3_rca": part3},
            str(docx_path),
        )
        html_path = result_docx.replace(".docx", ".html")

        if Path(result_docx).exists():
            print_ok(f"DOCX üretildi: {result_docx}")
        if Path(html_path).exists():
            print_ok(f"HTML üretildi: {html_path}")
    except Exception as e:
        print_warn(f"Rapor adımı uyarı verdi: {e}")

    # Özet json
    summary = {
        "timestamp": timestamp,
        "overall": "PASSED",
        "checks": {
            "type_of_event_forced": part2.get("type_of_event"),
            "immediate_cause_limit": immediate_cause_limit,
            "branch_count": len(branches),
            "why_lengths": why_lengths,
            "final_root_cause_count": len(part3.get("final_root_causes", [])),
        },
        "elapsed_seconds": round(time.time() - start, 2),
    }
    summary_file = output_dir / f"test_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print_ok(f"Test özeti: {summary_file}")

    print_header("SONUÇ")
    print_ok("Frontend type_of_event tabanlı dal limiti testi başarılı")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
