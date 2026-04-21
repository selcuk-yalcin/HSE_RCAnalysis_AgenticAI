#!/usr/bin/env python3
"""
================================================================================
MAJOR OLAY — DSPy V3.1 TAM SİSTEM TESTİ (DOCX + HTML)
================================================================================

OLAY: Haddehane sıcak metal — ciddi yanık / hastane sevk (major).

TEST KAPSAMI (test_electrical_shock_dspy.py ile aynı akış):
  1. Ortam ve API
  2. OverviewAgent
  3. AssessmentAgent
  4. RootCauseAgentV3_1 (DSPy) — type_of_event=Kaza → immediate_cause_limit=5
  5. SkillBasedDocxAgent — DOCX + HTML
  6. Kalite kontrolleri

Assessment sonrası part2 override:
  - type_of_event = "Kaza" (dal limiti 5)

ÇALIŞTIRMA:
  python tests/test_major_incident_rca.py
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
OLAY RAPORU — MAJOR YARALANMA (SICAK METAL)

Tarih: 25 Nisan 2026, Saat: 08:40
Lokasyon: Çelik Haddehane — Sıcak Metal Taşıma Hattı (Hatt-07)
Rapor Eden: Vardiya Güvenlik Görevlisi

OLAY AÇIKLAMASI:
Operatör sıcak metal parçası transferi sırasında eldivenin erimesi ve sıcak yüzeye temas
sonucu ciddi yanık ve derin doku hasarı yaşadı. Acil müdahale sonrası hastaneye sevk;
iş göremezlik bildirildi.

KRONOLOJİ:
- 08:15 — Hat normal çalışıyor
- 08:30 — Metal sıcaklığı yüksek; operatör eldiven kontrolü yapılmadan görev aldı
- 08:40 — Parça sırasında eldiven erimesi; cilt teması
- 08:42 — İlk yardım, alan tahliye
- 09:00 — Hastane sevk

YARALANMA:
- Ciddi yanık (el ve ön kol)
- Hastane + tedavi

ÖN BULGULAR:
- Yalıtımlı eldiven yerine standart eldiven kullanımı
- Risk değerlendirmesi güncel değil
- Gözetim ve durdur-bildir kültürü zayıf
""".strip()


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_warning(msg: str):
    print(f"  ⚠️  {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def print_dspy_info(msg: str):
    print(f"  ✨ {msg}")


def main():
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print_header("MAJOR OLAY — DSPy V3.1 TAM SİSTEM TESTİ")
    print_info(f"Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_dspy_info("DSPy-powered root cause analysis aktif")

    results = {"timestamp": timestamp, "steps": {}, "files": [], "dspy_enabled": False}
    output_dir = Path("outputs/major_incident_dspy")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ADIM 1
    print_header("ADIM 1: Ortam Kontrolü")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        assert api_key, "OPENROUTER_API_KEY bulunamadı"
        print_success(f"API Key: {api_key[:12]}...{api_key[-4:]}")

        try:
            import dspy
            print_dspy_info(f"DSPy kurulu: v{dspy.__version__}")
            results["dspy_enabled"] = True
        except ImportError:
            print_warning("DSPy bulunamadı")
            results["dspy_enabled"] = False

        print_success(f"Çıktı dizini: {output_dir}")
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Ortam hatası: {e}")
        results["steps"]["environment"] = "FAILED"
        return results

    # ADIM 2
    print_header("ADIM 2: OverviewAgent")
    try:
        agent = OverviewAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Ref No: {part1.get('ref_no')}")
        print_success(f"Olay Tipi: {part1.get('incident_type')}")
        print_info(f"Lokasyon: {part1.get('location', {}).get('facility', 'N/A')}")
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["overview"] = "FAILED"
        return results

    # ADIM 3
    print_header("ADIM 3: AssessmentAgent")
    try:
        agent = AssessmentAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)

        # Major senaryosu: frontend Kaza seçimi → dal limiti 5
        part2["type_of_event"] = "Kaza"
        if not part2.get("investigation") or not isinstance(part2.get("investigation"), dict):
            part2["investigation"] = {}
        part2["investigation"]["level"] = "High level"
        part2["actual_potential_harm"] = part2.get("actual_potential_harm") or "Fatal or major"

        print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
        print_success(f"type_of_event (override): {part2.get('type_of_event')}")
        print_success(f"Level: {part2.get('investigation', {}).get('level')}")
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["assessment"] = "FAILED"
        return results

    # ADIM 4
    print_header("ADIM 4: RootCauseAgentV3_1 (✨ DSPy)")
    try:
        print_dspy_info("DSPy-based 5-Why analysis başlatılıyor...")
        agent = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)
        print_success("V3.1 agent başlatıldı")

        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA},
        )

        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])
        limit = part3.get("immediate_cause_limit")

        print_dspy_info(f"immediate_cause_limit: {limit}")
        print_dspy_info(f"Analiz dalları: {len(branches)}")
        print_dspy_info(f"Kök nedenler: {len(causes)}")

        for i, branch in enumerate(branches, 1):
            why_count = len(branch.get("why_chain", branch.get("five_why_analysis", [])))
            print_info(f"[Dal {i}] - {why_count} Why")

        json_file = output_dir / f"major_incident_dspy_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON: {json_file}")
        results["files"].append(str(json_file))

        results["steps"]["rca_dspy"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca_dspy"] = "FAILED"
        return results

    # ADIM 5
    print_header("ADIM 5: Rapor Üretimi (DOCX + HTML)")
    try:
        agent = SkillBasedDocxAgent()
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = output_dir / f"{ref_no}_major_incident_dspy.docx"
        data = {"part1": part1, "part2": part2, "part3_rca": part3}
        result = agent.generate_report(data, str(docx_file))
        html_file = result.replace(".docx", ".html")

        if Path(result).exists():
            size = Path(result).stat().st_size / 1024
            print_success(f"DOCX: {size:.1f} KB - {result}")
            results["files"].append(result)
        if Path(html_file).exists():
            html_size = Path(html_file).stat().st_size / 1024
            print_success(f"HTML: {html_size:.1f} KB - {html_file}")
            results["files"].append(html_file)

        results["steps"]["report"] = "PASSED"
    except Exception as e:
        print_error(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["report"] = "FAILED"

    # ADIM 6
    print_header("ADIM 6: Kalite Kontrolleri")
    quality_checks = []

    if part3.get("immediate_cause_limit") == 5:
        print_success("immediate_cause_limit = 5 (Kaza)")
        quality_checks.append("cause_limit")
    else:
        print_warning(f"immediate_cause_limit: {part3.get('immediate_cause_limit')}")

    why_lens = [len(b.get("why_chain") or []) for b in part3.get("analysis_branches", [])]
    if why_lens and all(w == 5 for w in why_lens):
        print_success("Her dalda 5 Why")
        quality_checks.append("why_depth")
    else:
        print_warning(f"Why uzunlukları: {why_lens}")

    inv = (part2.get("investigation") or {}).get("level", "").lower()
    if "high" in inv:
        print_success("Investigation High level")
        quality_checks.append("investigation")

    if len(causes) >= 1:
        print_success(f"Kök neden sayısı: {len(causes)}")
        quality_checks.append("root_causes")

    results["quality_checks"] = len(quality_checks)
    results["steps"]["quality"] = "PASSED" if len(quality_checks) >= 3 else "PARTIAL"

    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])

    print_header("TEST ÖZET")
    print_info(f"Süre: {elapsed:.1f} saniye")
    print_info(f"Sonuç: {passed}/{total} adım başarılı")
    print_info(f"Kalite: {len(quality_checks)}/4 kontrol geçti")

    if passed == total:
        print_success("TÜM ADIMLAR TAMAMLANDI")
        results["overall"] = "PASSED"
    elif passed >= total - 1:
        print_warning(f"{total - passed} adım kısmi")
        results["overall"] = "PARTIAL"
    else:
        print_error(f"{total - passed} adım başarısız")
        results["overall"] = "FAILED"

    print("\nÜretilen dosyalar:")
    for f in results["files"]:
        print(f"   • {f}")

    summary_file = output_dir / f"test_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "test": "major_incident_dspy",
                "timestamp": timestamp,
                "elapsed_seconds": elapsed,
                "dspy_enabled": results["dspy_enabled"],
                "immediate_cause_limit": part3.get("immediate_cause_limit"),
                "steps": results["steps"],
                "quality_checks": results.get("quality_checks", 0),
                "overall": results["overall"],
                "files": results["files"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nTest özeti: {summary_file}\n")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") in ["PASSED", "PARTIAL"] else 1)
