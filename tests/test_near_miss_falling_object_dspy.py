#!/usr/bin/env python3
"""
================================================================================
DÜŞEN PARÇA / RAMAK KALA — DSPy V3.1 TAM SİSTEM TESTİ
================================================================================

OLAY TANIMI:
  Üretim hattı girişinde sarmal kapı mekanizmasından metal bağlantı parçası koparak
  yakındaki çalışanın yanına (~1,5 m) düştü. Yaralanma olmadı; potansiyel ciddi
  darbe riski. Bakım ve periyodik kontrol eksikliği şüphesi.

TEST KAPSAMI:
  (test_electrical_shock_dspy.py ile aynı akış)
  1. Ortam ve API kontrolleri
  2. OverviewAgent
  3. AssessmentAgent
  4. RootCauseAgentV3_1 (DSPy)
  5. SkillBasedDocxAgent (DOCX + HTML)
  6. Çıktı kalite kontrolü (olaya özel esnek kriterler)

ÇALIŞTIRMA:
  conda activate hse_dspy
  python tests/test_near_miss_falling_object_dspy.py
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


# ============================================================================
# INCIDENT DATA — DÜŞEN PARÇA / RAMAK KALA
# ============================================================================

INCIDENT_DATA = """
OLAY RAPORU — SARMAL KAPI MEKANİZMASINDAN DÜŞEN PARÇA (RAMAK KALA)

Tarih: 18 Mart 2026, Saat: 08:42
Lokasyon: Üretim Tesisi — Ana Giriş, Sarmal Kapı Bölgesi (SK-01)
Rapor Eden: Vardiya Güvenlik Görevlisi — Selin Korkmaz

OLAY AÇIKLAMASI:
Sabah vardiyasında işçiler girişte beklerken sarmal kapının üst mekanizmasından
metal bir bağlantı braketi koparak yere düştü. Parça, yaklaşık 1,5 metre
mesafede duran depo operatörü Mehmet Öz (34) yanına düştü; çarpma olmadı.
Olay anında anormal metalik ses duyuldu; kapı çalışmaya devam etti.

OLAY KRONOLOJİSİ:
- 08:35 — Kapı normal çalışıyor, yoğun personel girişi
- 08:40 — Birkaç kişi "tıkırtı" sesinden bahsetti
- 08:42 — Braket kopup zemine düştü; bölge tahliye edildi
- 08:45 — Alan şeritlendi, kapı güvenli şekilde kapatıldı
- 09:00 — Bakım müdahalesi, kopan parça mühürlendi
- 09:30 — Olay kaydı ve ramak kala bildirimi tamamlandı

ETKİLENEN KİŞİ:
- Mehmet Öz, 34, depo operatörü — fiziksel yaralanma YOK; psikolojik şok bildirimi

HASAR:
- Kişisel yaralanma yok
- Üretim duruşu: ~45 dk (kapı güvenlik kontrolü)

GÜVENLİK / PROSEDÜR NOTLARI:
- Sarmal kapı periyodik bakım planı: kağıtta aylık; son detaylı mekanizma
  kontrolü 14 ay önce kayıtlarda görünüyor
- Anormal ses/titreşim için "durdur-bildir" prosedürü zayıf uygulanıyor
- Bakım kayıtları kısmen eksik; kritik bağlantı tork kontrolü yapılmıyor

ÖN BULGULAR (KÖK NEDEN TASLAK):
1. Mekanik aşınma / gevşeme zamanında tespit edilmedi
2. Bakım önceliği düşük; üretim girişi aksamasın baskısı
3. Çalışanların anormal sesi ciddiye alma eğitimi yetersiz

TANIK:
- "Ses bir süredir vardı ama aceleyle içeri girdik." — İsimsiz çalışan beyanı
"""


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
    """Run near-miss / falling object pipeline test with DSPy V3.1."""

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print_header("DÜŞEN PARÇA / RAMAK KALA — DSPy V3.1 TAM SİSTEM TESTİ")
    print_info(f"Test Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Olay: Sarmal kapı mekanizması — kopan parça, yaralanma yok")
    print_dspy_info("DSPy-powered root cause analysis aktif")

    results = {"timestamp": timestamp, "steps": {}, "files": [], "dspy_enabled": False}
    output_dir = Path("outputs/near_miss_falling_dspy")

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
            print_warning("DSPy bulunamadı, V2 fallback kullanılacak")
            results["dspy_enabled"] = False

        output_dir.mkdir(parents=True, exist_ok=True)
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
        print_success("Agent başlatıldı")

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

        print_success(f"Şiddet: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
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

        agent = RootCauseAgentV3_1(
            use_rag=False,
            enable_diversity_check=True,
        )
        print_success("V3.1 agent başlatıldı")

        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA},
        )

        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])

        print_dspy_info(f"Analiz dalları: {len(branches)}")
        print_dspy_info(f"Kök nedenler: {len(causes)}")

        for i, branch in enumerate(branches, 1):
            branch_name = branch.get("branch_name", f"Branch {i}")
            why_count = len(
                branch.get("why_chain", branch.get("five_why_analysis", []))
            )
            print_info(f"[Dal {i}] {branch_name} - {why_count} Why")

        print_info("Kök nedenler:")
        for i, rc in enumerate(causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = (rc.get("root_cause_title", "N/A") or "")[:60]
            print_info(f"  [{i}] {code} - {title}")

        json_file = output_dir / f"near_miss_falling_dspy_{timestamp}.json"
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
        docx_file = output_dir / f"{ref_no}_near_miss_falling_dspy.docx"

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

    # ADIM 6 — esnek kalite (ramak kala / düşen parça)
    print_header("ADIM 6: Kalite Kontrolleri")
    quality_checks = []

    itype = (part1.get("incident_type") or "").lower()
    if "near" in itype or "miss" in itype or "ramak" in itype or "minor" in itype:
        print_success(f"Olay tipi senaryoya uygun görünüyor: {part1.get('incident_type')}")
        quality_checks.append("incident_type_plausible")
    else:
        print_warning(f"Olay tipi (LLM): {part1.get('incident_type')}")

    part3_str = json.dumps(part3, ensure_ascii=False).lower()
    if any(
        k in part3_str
        for k in ("bakım", "bakim", "kapı", "kapi", "mekaniz", "parça", "parca", "aşın", "asin")
    ):
        print_success("Analiz metninde bakım / mekanizma / parça teması var")
        quality_checks.append("domain_keywords")
    else:
        print_warning("Beklenen anahtar kelimeler zayıf")

    if len(branches) >= 1:
        print_success(f"En az bir analiz dalı ({len(branches)})")
        quality_checks.append("branches")
    else:
        print_warning("Dal sayısı düşük")

    if len(causes) >= 1:
        print_success(f"Kök neden sayısı: {len(causes)}")
        quality_checks.append("root_causes")
    else:
        print_warning("Kök neden listesi boş veya eksik")

    results["quality_checks"] = len(quality_checks)
    results["steps"]["quality"] = "PASSED" if len(quality_checks) >= 3 else "PARTIAL"

    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])

    print_header("TEST ÖZET")
    print_info(f"Süre: {elapsed:.1f} saniye")
    print_info(f"Sonuç: {passed}/{total} adım başarılı")
    print_info(f"Kalite: {len(quality_checks)}/4 kontrol geçti")

    if results["dspy_enabled"]:
        print_dspy_info("DSPy V3.1 kullanıldı")

    if passed == total:
        print_success("TÜM ADIMLAR TAMAMLANDI")
        results["overall"] = "PASSED"
    elif passed >= total - 1:
        print_warning(f"{total - passed} adım kısmi / uyarı")
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
                "test": "near_miss_falling_object_dspy",
                "timestamp": timestamp,
                "elapsed_seconds": elapsed,
                "dspy_enabled": results["dspy_enabled"],
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
