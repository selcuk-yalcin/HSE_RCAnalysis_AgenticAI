#!/usr/bin/env python3
"""
================================================================================
TRAIN ODOR INCIDENT — DSPy V3.1 FULL SYSTEM TEST
================================================================================

SCENARIO:
  During a train journey from Hannover, a passenger (Selcuk Yalcin) had strong
  foot odor in the carriage. Nearby passengers avoided adjacent seats. A nearby
  passenger (Mrs. Marina Chai) reported dizziness and briefly fainted.

TEST SCOPE:
  (same pipeline shape as test_near_miss_falling_object_dspy.py)
  1. Environment and API checks
  2. OverviewAgent
  3. AssessmentAgent
  4. RootCauseAgentV3_1 (DSPy)
  5. SkillBasedDocxAgent (DOCX + HTML)
  6. Scenario-focused quality checks

RUN:
  conda activate hse_dspy
  python tests/test_train_odor_incident_dspy.py
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
# INCIDENT DATA — TRAIN ODOR / PASSENGER HEALTH COMPLAINT
# ============================================================================

INCIDENT_DATA = """
INCIDENT REPORT — TRAIN CARRIAGE ODOR EXPOSURE AND PASSENGER FAINTING

Date: 23 April 2026, Time: 16:35
Location: Intercity Train (Hannover to destination), Carriage B, Seat Zone 12-18
Reported By: On-board Service Supervisor

INCIDENT DESCRIPTION:
During routine service rounds, staff observed multiple passengers avoiding seats
near one passenger, Mr. Selcuk Yalcin, due to strong foot odor in the area.
Mrs. Marina Chai, seated nearby, reported nausea, dizziness, and then briefly
lost consciousness for approximately 20-30 seconds.

TIMELINE:
- 16:20 — Carriage occupancy high, no formal complaints logged
- 16:30 — Passengers begin informal seat changes away from affected area
- 16:33 — First verbal complaint about strong odor received by staff
- 16:35 — Mrs. Marina Chai reports dizziness and faints briefly
- 16:36 — Staff apply first response protocol; passenger moved to fresh-air zone
- 16:40 — Passenger regains full consciousness; hydration and monitoring provided
- 16:55 — Incident formally documented and escalated to operations

PEOPLE INVOLVED:
- Selcuk Yalcin (passenger) — source area associated with odor complaint
- Mrs. Marina Chai (passenger) — temporary fainting episode, recovered
- On-board service team — response and escalation

IMMEDIATE IMPACT:
- Temporary medical concern (brief fainting)
- Passenger discomfort and seat displacement
- Service disruption in affected carriage area

SAFETY / PROCEDURAL NOTES:
- No clear protocol for non-chemical but severe odor complaints in enclosed spaces
- Delayed escalation from first complaint to active intervention
- Ventilation adjustment and relocation actions were reactive, not proactive

PRELIMINARY ROOT-CAUSE HYPOTHESES:
1. Inadequate early detection/escalation for passenger environmental discomfort
2. Lack of specific SOP for odor-related health-risk situations
3. Delayed operational controls (ventilation/seat relocation/zone isolation)

WITNESS NOTE:
"People were standing rather than sitting near that row before the collapse."
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
    """Run train odor passenger-health incident test with DSPy V3.1."""

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print_header("TRAIN ODOR INCIDENT — DSPy V3.1 FULL SYSTEM TEST")
    print_info(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Scenario: enclosed carriage odor exposure and temporary fainting")
    print_dspy_info("DSPy-powered root cause analysis active")

    results = {"timestamp": timestamp, "steps": {}, "files": [], "dspy_enabled": False}
    output_dir = Path("outputs/train_odor_incident_dspy")

    # STEP 1
    print_header("STEP 1: Environment Check")
    try:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        assert api_key, "OPENROUTER_API_KEY / OPENAI_API_KEY not found"
        print_success(f"API Key: {api_key[:12]}...{api_key[-4:]}")

        try:
            import dspy

            print_dspy_info(f"DSPy installed: v{dspy.__version__}")
            results["dspy_enabled"] = True
        except ImportError:
            print_warning("DSPy not found, V2 fallback may be used")
            results["dspy_enabled"] = False

        output_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Output directory: {output_dir}")

        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Environment error: {e}")
        results["steps"]["environment"] = "FAILED"
        return results

    # STEP 2
    print_header("STEP 2: OverviewAgent")
    try:
        agent = OverviewAgent()
        print_success("Agent initialized")

        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Ref No: {part1.get('ref_no')}")
        print_success(f"Incident Type: {part1.get('incident_type')}")
        print_info(f"Location: {part1.get('location', {}).get('facility', 'N/A')}")

        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        results["steps"]["overview"] = "FAILED"
        return results

    # STEP 3
    print_header("STEP 3: AssessmentAgent")
    try:
        agent = AssessmentAgent()
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)

        print_success(f"Harm Level: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Investigation Level: {part2.get('investigation', {}).get('level')}")

        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        results["steps"]["assessment"] = "FAILED"
        return results

    # STEP 4
    print_header("STEP 4: RootCauseAgentV3_1 (DSPy)")
    try:
        print_dspy_info("Starting DSPy-based 5-Why analysis...")

        agent = RootCauseAgentV3_1(
            use_rag=False,
            enable_diversity_check=True,
        )
        print_success("V3.1 agent initialized")

        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA},
        )

        branches = part3.get("analysis_branches", [])
        causes = part3.get("final_root_causes", [])

        print_dspy_info(f"Branches: {len(branches)}")
        print_dspy_info(f"Root causes: {len(causes)}")

        for i, branch in enumerate(branches, 1):
            branch_name = branch.get("branch_name", f"Branch {i}")
            why_count = len(branch.get("why_chain", branch.get("five_why_analysis", [])))
            print_info(f"[Branch {i}] {branch_name} - {why_count} Why")

        print_info("Final root causes:")
        for i, rc in enumerate(causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = (rc.get("root_cause_title", "N/A") or "")[:70]
            print_info(f"  [{i}] {code} - {title}")

        json_file = output_dir / f"train_odor_incident_dspy_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON: {json_file}")
        results["files"].append(str(json_file))

        results["steps"]["rca_dspy"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        results["steps"]["rca_dspy"] = "FAILED"
        return results

    # STEP 5
    print_header("STEP 5: Report Generation (DOCX + HTML)")
    try:
        agent = SkillBasedDocxAgent()

        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_file = output_dir / f"{ref_no}_train_odor_incident_dspy.docx"

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
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        results["steps"]["report"] = "FAILED"

    # STEP 6 — flexible quality checks (odor / enclosed-space / response flow)
    print_header("STEP 6: Quality Checks")
    quality_checks = []

    itype = (part1.get("incident_type") or "").lower()
    if any(k in itype for k in ("incident", "ill", "health", "near", "minor")):
        print_success(f"Incident type looks plausible: {part1.get('incident_type')}")
        quality_checks.append("incident_type_plausible")
    else:
        print_warning(f"Incident type (LLM): {part1.get('incident_type')}")

    part3_str = json.dumps(part3, ensure_ascii=False).lower()
    if any(
        k in part3_str
        for k in ("odor", "hygiene", "ventilation", "enclosed", "passenger", "escalation", "response")
    ):
        print_success("Analysis includes expected scenario themes")
        quality_checks.append("domain_keywords")
    else:
        print_warning("Expected domain keywords are weak")

    if len(branches) >= 1:
        print_success(f"At least one analysis branch ({len(branches)})")
        quality_checks.append("branches")
    else:
        print_warning("Branch count is low")

    if len(causes) >= 1:
        print_success(f"Root cause count: {len(causes)}")
        quality_checks.append("root_causes")
    else:
        print_warning("Root cause list is empty")

    results["quality_checks"] = len(quality_checks)
    results["steps"]["quality"] = "PASSED" if len(quality_checks) >= 3 else "PARTIAL"

    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])

    print_header("TEST SUMMARY")
    print_info(f"Elapsed: {elapsed:.1f} seconds")
    print_info(f"Result: {passed}/{total} steps passed")
    print_info(f"Quality: {len(quality_checks)}/4 checks passed")

    if results["dspy_enabled"]:
        print_dspy_info("DSPy V3.1 was used")

    if passed == total:
        print_success("ALL STEPS COMPLETED")
        results["overall"] = "PASSED"
    elif passed >= total - 1:
        print_warning(f"{total - passed} step(s) partial/warning")
        results["overall"] = "PARTIAL"
    else:
        print_error(f"{total - passed} step(s) failed")
        results["overall"] = "FAILED"

    print("\nGenerated files:")
    for f in results["files"]:
        print(f"   • {f}")

    summary_file = output_dir / f"test_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "test": "train_odor_incident_dspy",
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
    print(f"\nTest summary: {summary_file}\n")

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") in ["PASSED", "PARTIAL"] else 1)
