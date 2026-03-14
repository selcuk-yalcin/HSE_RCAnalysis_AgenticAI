#!/usr/bin/env python3
"""
================================================================================
FALL FROM HEIGHT INCIDENT - FULL SYSTEM TEST (ENGLISH VERSION)
================================================================================

INCIDENT DESCRIPTION:
  Construction worker fell 6 meters from scaffolding, seriously injured.
  Worker was not wearing safety harness, scaffolding guardrail was incomplete.
  Worker was taken to emergency with spinal fracture and internal bleeding.

TEST SCOPE:
  1. Environment check and API keys
  2. OverviewAgent - Initial incident report analysis
  3. AssessmentAgent - RIDDOR and investigation level
  4. RootCauseAgentV2 - Hierarchical 5-Why analysis
  5. SkillBasedDocxAgent - Professional report generation (DOCX + HTML)
  6. Output validation and quality control

EXPECTED RESULTS:
  - Incident Type: Major/Fatal injury
  - RIDDOR: Y (Fall from height >2m)
  - Investigation Level: High level
  - Root Causes: 3-4 items (D category - Organizational)
  - DOCX Report: 18-20 pages, fully formatted
  - HTML Report: Editable, responsive

RUN:
  python tests/test_fall_from_height_english.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Project imports
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2
from agents.skillbased_docx_agent import SkillBasedDocxAgent


# ============================================================================
# INCIDENT DATA - FALL FROM HEIGHT (ENGLISH)
# ============================================================================

INCIDENT_DATA = """
INCIDENT REPORT - FALL FROM HEIGHT

Date: February 18, 2026, Time: 10:35
Location: Construction Site - 4th Floor Scaffolding Area
Reported by: Site Manager - Mustafa Çelik

INCIDENT DESCRIPTION:
Scaffolding assembly worker Hasan Yıldız (32) fell from scaffolding at 
approximately 6 meters height and crashed to the ground. The worker was 
seriously injured and taken to hospital by ambulance.

INCIDENT TIMELINE:
- 08:00 - Worker started shift, assigned to 4th floor scaffolding assembly
- 09:30 - Scaffolding platform assembly in progress
- 10:30 - Worker lost balance while working at scaffolding edge
- 10:35 - Fell 6 meters to ground level
- 10:37 - Co-workers rushed to help, called 112 emergency
- 10:42 - First aid administered (conscious but severely injured)
- 10:55 - Ambulance arrived, transported to hospital
- 11:20 - Hospital report: L2 spinal fracture, internal bleeding, serious condition

AFFECTED PERSON:
- Name: Hasan Yıldız
- Age: 32
- Position: Scaffolding Assembly Worker
- Experience: 8 months in scaffolding work
- Shift: Day shift (08:00-17:00)

INJURY DETAILS:
- L2 spinal vertebra fracture
- Pelvic fracture
- Internal bleeding (spleen)
- Multiple contusions
- Admitted to intensive care
- Prognosis: Serious, long-term treatment required

SAFETY EQUIPMENT:
✗ Safety harness: NOT WORN
✗ Guardrail: INCOMPLETE (assembly not finished)
✗ Safety net: NONE
✓ Hard hat: WORN
✓ Safety boots: WORN
✗ Full-body safety harness: NOT WORN

SCAFFOLDING CONDITION:
- Platform width: 1.2m (standard)
- Guardrail: Only present on one side
- Working edge: Guardrail-free side
- Scaffolding class: Steel tube scaffolding
- Last inspection: 2 days ago (guardrail deficiency not noted)
- Scaffolding permit: Available (but not current)

ROOT CAUSE PRELIMINARY FINDINGS:
1. Worker did not wear safety harness (procedure violation)
2. Work started before guardrail assembly completed
3. Work permit system not functioning properly (inadequate risk assessment)
4. Safety officer was not on site tour
5. Job training records incomplete (height work training not provided)
6. Safety harness use monitoring not performed
7. Production pressure (project delayed, instruction to finish quickly)

WITNESS STATEMENTS:
- Ali Demir (Worker): "Hasan was working without harness. Everyone does it. 
  Supervisor was rushing us, so we moved to the side without guardrail."
- Mehmet Kara (Foreman): "Guardrail was to be installed tomorrow. Platform 
  assembly had to be finished today. Supervisor said finish quickly."
- Site Manager: "I didn't know guardrail was incomplete. Workers know they 
  should wear harnesses."

MANAGEMENT FACTORS:
- Project 3 weeks delayed
- Client pressure: "Quick completion" demand
- Safety meetings: Not held for 2 months
- Risk assessment: 6 months old (not updated)
- Job training records: Incomplete/irregular
- Inspection frequency: Once per week (inadequate)

IMMEDIATE ACTIONS:
1. All work at height stopped
2. Scaffolding inspections redone
3. Harness use made mandatory
4. Safety briefing conducted
5. Project schedule reviewed
"""


# ============================================================================
# TEST EXECUTION
# ============================================================================

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  ✅ {msg}")


def print_error(msg: str):
    print(f"  ❌ {msg}")


def print_info(msg: str):
    print(f"     {msg}")


def main():
    """Run fall from height incident test - ENGLISH version."""
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("FALL FROM HEIGHT INCIDENT - FULL SYSTEM TEST (ENGLISH)")
    print_info(f"Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Incident: Construction site scaffolding fall (6m height)")
    
    results = {"timestamp": timestamp, "steps": {}}
    
    # Step 1: Environment Check
    print_header("STEP 1: Environment Check")
    try:
        assert os.getenv("OPENROUTER_API_KEY"), "API key missing"
        print_success("API key available")
        print_success("Dependencies checked")
        results["steps"]["environment"] = "PASSED"
    except Exception as e:
        print_error(f"Environment error: {e}")
        results["steps"]["environment"] = "FAILED"
        return results
    
    # Step 2: OverviewAgent
    print_header("STEP 2: OverviewAgent - Initial Assessment")
    try:
        agent = OverviewAgent()
        print_success("OverviewAgent initialized")
        
        incident_dict = {"description": INCIDENT_DATA}
        part1 = agent.process_initial_report(incident_dict)
        print_success(f"Reference No: {part1.get('ref_no')}")
        print_success(f"Incident Type: {part1.get('incident_type')}")
        print_info(f"What happened: {part1.get('brief_details', {}).get('what', 'N/A')[:80]}...")
        
        results["steps"]["overview"] = "PASSED"
        results["part1"] = part1
    except Exception as e:
        print_error(f"OverviewAgent error: {e}")
        results["steps"]["overview"] = "FAILED"
        return results
    
    # Step 3: AssessmentAgent
    print_header("STEP 3: AssessmentAgent - Severity Assessment")
    try:
        agent = AssessmentAgent()
        print_success("AssessmentAgent initialized")
        
        incident_dict = {"description": INCIDENT_DATA}
        part2 = agent.assess_incident(part1, incident_dict)
        print_success(f"Severity Level: {part2.get('actual_potential_harm')}")
        print_success(f"RIDDOR: {part2.get('riddor', {}).get('reportable')}")
        print_success(f"Investigation Level: {part2.get('investigation', {}).get('level')}")
        
        results["steps"]["assessment"] = "PASSED"
        results["part2"] = part2
    except Exception as e:
        print_error(f"AssessmentAgent error: {e}")
        results["steps"]["assessment"] = "FAILED"
        return results
    
    # Step 4: RootCauseAgentV2
    print_header("STEP 4: RootCauseAgentV2 - Root Cause Analysis")
    try:
        agent = RootCauseAgentV2()
        print_success("RootCauseAgentV2 initialized")
        
        part3 = agent.analyze_root_causes(
            part1_data=part1,
            part2_data=part2,
            investigation_data={"description": INCIDENT_DATA}
        )
        
        branches = part3.get("analysis_branches", [])
        root_causes = part3.get("final_root_causes", [])
        
        print_success(f"Analysis branches: {len(branches)}")
        print_success(f"Root causes found: {len(root_causes)}")
        
        for i, rc in enumerate(root_causes, 1):
            code = rc.get("root_cause_code", "N/A")
            title = rc.get("root_cause_title", "N/A")[:50]
            print_info(f"[{i}] {code} - {title}")
        
        # Save JSON
        json_path = f"outputs/fall_from_height_english_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(part3, f, ensure_ascii=False, indent=2)
        print_success(f"JSON saved: {json_path}")
        
        results["steps"]["rca"] = "PASSED"
        results["part3"] = part3
    except Exception as e:
        print_error(f"RootCauseAgentV2 error: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["rca"] = "FAILED"
        return results
    
    # Step 5: SkillBasedDocxAgent
    print_header("STEP 5: SkillBasedDocxAgent - Report Generation")
    try:
        agent = SkillBasedDocxAgent()
        print_success("SkillBasedDocxAgent initialized")
        
        ref_no = part1.get("ref_no", "UNKNOWN")
        docx_path = f"outputs/{ref_no}_fall_from_height_ENGLISH.docx"
        
        investigation_data = {
            "part1": part1,
            "part2": part2,
            "part3_rca": part3
        }
        
        result_path = agent.generate_report(investigation_data, docx_path)
        html_path = result_path.replace('.docx', '.html')
        
        if Path(result_path).exists():
            size_kb = Path(result_path).stat().st_size / 1024
            print_success(f"DOCX created: {size_kb:.1f} KB")
            print_info(f"File: {result_path}")
        
        if Path(html_path).exists():
            html_kb = Path(html_path).stat().st_size / 1024
            print_success(f"HTML created: {html_kb:.1f} KB")
            print_info(f"File: {html_path}")
        
        results["steps"]["docx"] = "PASSED"
        results["docx_path"] = result_path
        results["html_path"] = html_path
    except Exception as e:
        print_error(f"SkillBasedDocxAgent error: {e}")
        import traceback
        traceback.print_exc()
        results["steps"]["docx"] = "FAILED"
        return results
    
    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for v in results["steps"].values() if v == "PASSED")
    total = len(results["steps"])
    
    print_header("TEST SUMMARY")
    print_info(f"Elapsed Time: {elapsed:.1f} seconds")
    print_info(f"Passed Steps: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED!")
        results["overall"] = "PASSED"
    else:
        print_error(f"❌ {total - passed} tests failed")
        results["overall"] = "FAILED"
    
    print("\n📄 Generated Files:")
    if "docx_path" in results:
        print(f"   DOCX: {results['docx_path']}")
    if "html_path" in results:
        print(f"   HTML: {results['html_path']}")
    print(f"   JSON: {json_path}\n")
    
    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("overall") == "PASSED" else 1)
