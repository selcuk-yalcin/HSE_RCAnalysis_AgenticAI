#!/usr/bin/env python3
"""
DYNAMIC IMMEDIATE-CAUSE TESTS (Severity-based)

İki basit olay senaryosu ile RootCauseAgentV3_1'in ciddiyete göre
immediate-cause (dal) limitini doğrular:
- Damage only  -> immediate_cause_limit = 2
- Fatal/Major  -> immediate_cause_limit = 5

Not: Why zinciri her dalda sabit 5 adım olmalıdır.

Çalıştırma:
  python tests/test_dynamic_why_severity_cases.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv olmayan ortamlarda da test dosyası açılabilsin
    pass

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
except ModuleNotFoundError as e:
    missing = getattr(e, "name", "")
    print(
        f"❌ Eksik bağımlılık: {missing}. "
        "Önce proje bağımlılıklarını kurun (örn. pip install -r requirements.txt)."
    )
    raise


def run_case(
    agent: RootCauseAgentV3_1,
    name: str,
    description: str,
    event_type: str,
    severity: str,
    inv_level: str,
    expected_limit: int,
):
    print("\n" + "=" * 80)
    print(f"CASE: {name}")
    print("=" * 80)
    print(f"Event Type: {event_type}")
    print(f"Severity: {severity}")
    print(f"Investigation Level: {inv_level}")
    print(f"Expected immediate_cause_limit: {expected_limit}")

    part1 = {
        "ref_no": f"CASE-{datetime.now().strftime('%H%M%S')}",
        "incident_type": "Near-miss" if expected_limit <= 2 else "Major injury",
        "description": description,
    }
    part2 = {
        "type_of_event": event_type,
        "actual_potential_harm": severity,
        "investigation": {"level": inv_level},
    }
    inv_data = {"description": description}

    result = agent.analyze_root_causes(
        part1_data=part1,
        part2_data=part2,
        investigation_data=inv_data,
        synthesize_meta_root=True,
    )

    actual_limit = result.get("immediate_cause_limit")
    branches = result.get("analysis_branches", [])
    final_roots = result.get("final_root_causes", [])
    branch_lengths = [len((b.get("why_chain") or [])) for b in branches]

    print(f"Actual immediate_cause_limit: {actual_limit}")
    print(f"Branch count: {len(branches)}")
    print(f"Final root cause count: {len(final_roots)}")
    print(f"Why lengths per branch: {branch_lengths}")

    assert actual_limit == expected_limit, (
        f"immediate_cause_limit mismatch! expected={expected_limit}, actual={actual_limit}"
    )

    # Why zinciri sabit: her dal tam 5 Why içermeli
    assert all(length == 5 for length in branch_lengths), (
        f"Unexpected why lengths: {branch_lengths}, expected all=5"
    )

    # Root-cause sayısı, hedef aralıkta olmalı (2..limit)
    assert 2 <= len(final_roots) <= expected_limit, (
        f"final_root_causes out of range: {len(final_roots)} (limit={expected_limit})"
    )

    print("✅ CASE PASSED")


def main():
    print("\nDynamic immediate-cause severity test başlıyor...")

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY / OPENAI_API_KEY bulunamadı")
        return 1

    agent = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)

    damage_only_description = """
Üretim alanında forklift geri manevra sırasında plastik koruyucu bariyere çarptı.
Yaralanma olmadı. Sadece bariyerde çatlak oluştu ve 15 dakikalık iş kesintisi yaşandı.
Acil durumda alan izole edildi, hasarlı bariyer değiştirildi.
""".strip()

    major_description = """
Bakım teknisyeni yüksek platformda çalışma sırasında dengesini kaybetti,
emniyet kemeri olmasına rağmen sert şekilde platforma çarptı. Çoklu kırık ve
ciddi travma nedeniyle hastaneye sevk edildi. Olay major injury olarak değerlendirildi.
""".strip()

    # Ramak Kala -> limit 2 (frontend type_of_event önceliği)
    run_case(
        agent=agent,
        name="Near-miss incident",
        description=damage_only_description,
        event_type="Ramak Kala Olay",
        severity="Damage only",
        inv_level="Basic",
        expected_limit=2,
    )

    # Kaza -> limit 5 (frontend type_of_event önceliği)
    run_case(
        agent=agent,
        name="Accident / major incident",
        description=major_description,
        event_type="Kaza",
        severity="Fatal or major",
        inv_level="High level",
        expected_limit=5,
    )

    print("\n🎉 Tüm severity-case testleri geçti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
