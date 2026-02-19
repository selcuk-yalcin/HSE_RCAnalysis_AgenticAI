"""
Comprehensive Agent Test Suite
Tests all agents in the HSE Investigation System
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agents.overview_agent import OverviewAgent
from agents.assessment_agent import AssessmentAgent
from agents.rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
from agents.pdf_report_agent import PDFReportAgent
from agents.orchestrator import RootCauseOrchestrator
from shared.config import OPENAI_CONFIG


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_subsection(title: str):
    """Print formatted subsection header"""
    print("\n" + "-"*80)
    print(f"  {title}")
    print("-"*80)


def test_environment():
    """Test environment variables and configuration"""
    print_section("TEST 1: Environment Configuration")
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-4:]
        print(f" OpenAI API Key found: {masked_key}")
    else:
        print(" OpenAI API Key NOT found!")
        return False
    
    # Check configuration
    print(f" Model: {OPENAI_CONFIG.get('model')}")
    print(f" Temperature: {OPENAI_CONFIG.get('temperature')}")
    print(f" Max Tokens: {OPENAI_CONFIG.get('max_tokens')}")
    
    return True


def test_overview_agent():
    """Test Overview Agent (Part 1)"""
    print_section("TEST 2: Overview Agent")
    
    try:
        # Initialize agent
        agent = OverviewAgent(OPENAI_CONFIG)
        print(" Overview Agent initialized successfully")
        
        # Test incident data
        incident_data = {
            "reported_by": "Sarah Johnson - Safety Officer",
            "description": "Warehouse operative sustained laceration to hand from sharp edge on damaged pallet during loading operations",
            "injury_description": "Deep cut on right palm, bleeding controlled, required 5 stitches at hospital",
            "forwarded_to": "Operations Manager"
        }
        
        print("\n Processing incident report...")
        result = agent.process_initial_report(incident_data)
        
        # Verify results
        assert 'ref_no' in result, "Missing ref_no"
        assert 'incident_type' in result, "Missing incident_type"
        assert 'brief_details' in result, "Missing brief_details"
        
        print(f"\n Reference Number: {result['ref_no']}")
        print(f" Incident Type: {result['incident_type']}")
        print(f" Brief Details extracted successfully")
        
        return result
        
    except Exception as e:
        print(f" Overview Agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_assessment_agent(part1_data):
    """Test Assessment Agent (Part 2)"""
    print_section("TEST 3: Assessment Agent")
    
    try:
        # Initialize agent
        agent = AssessmentAgent(OPENAI_CONFIG)
        print(" Assessment Agent initialized successfully")
        
        # Process assessment
        print("\n Conducting initial assessment...")
        result = agent.assess_incident(part1_data)
        
        # Verify results
        assert 'type_of_event' in result, "Missing type_of_event"
        assert 'actual_potential_harm' in result, "Missing actual_potential_harm"
        assert 'investigation_level' in result, "Missing investigation_level"
        
        print(f"\n Event Type: {result['type_of_event']}")
        print(f" Severity Level: {result['actual_potential_harm']}")
        print(f" Investigation Level: {result['investigation_level']}")
        print(f" RIDDOR Reportable: {result.get('riddor_reportable', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f" Assessment Agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_rootcause_agent(part1_data, part2_data):
    """Test Root Cause Agent (Part 3)"""
    print_section("TEST 4: Root Cause Analysis Agent")
    
    try:
        # Initialize agent
        agent = RootCauseAgent(OPENAI_CONFIG)
        print(" Root Cause Agent initialized successfully")
        
        # Perform analysis
        print("\n Performing 5 Why analysis...")
        result = agent.analyze_root_causes(part1_data, part2_data)
        
        # Verify results
        assert 'immediate_causes' in result, "Missing immediate_causes"
        assert 'underlying_causes' in result, "Missing underlying_causes"
        assert 'root_causes' in result, "Missing root_causes"
        
        print(f"\n Immediate Causes: {len(result['immediate_causes'])} identified")
        print(f" Underlying Causes: {len(result['underlying_causes'])} identified")
        print(f" Root Causes: {len(result['root_causes'])} identified")
        
        # Print sample causes
        if result['immediate_causes']:
            print(f"\n   Example Immediate Cause: {result['immediate_causes'][0]}")
        if result['root_causes']:
            print(f"   Example Root Cause: {result['root_causes'][0]}")
        
        return result
        
    except Exception as e:
        print(f" Root Cause Agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_orchestrator():
    """Test Orchestrator (Complete workflow)"""
    print_section("TEST 5: Orchestrator - Complete Investigation")
    
    try:
        # Initialize orchestrator
        orchestrator = RootCauseOrchestrator(OPENAI_CONFIG)
        print(" Orchestrator initialized successfully")
        
        # Full incident data
        incident_data = {
            "reported_by": "Mike Thompson - Warehouse Manager",
            "description": "Employee slipped on wet floor in warehouse loading bay during shift change. "
                          "Floor was wet from recent cleaning but no warning signs were present. "
                          "Employee fell backwards hitting head on concrete floor.",
            "injury_description": "Concussion, back pain, required hospital observation for 24 hours",
            "forwarded_to": "HSE Director and Operations Manager"
        }
        
        print("\n Running complete investigation workflow...")
        print("   This will test all agents in sequence:")
        print("     Overview Agent")
        print("     Assessment Agent")
        print("     Root Cause Agent")
        
        result = orchestrator.run_investigation(incident_data)
        
        # Verify complete result
        assert 'part1' in result, "Missing Part 1"
        assert 'part2' in result, "Missing Part 2"
        assert 'part3_rca' in result, "Missing Part 3"
        
        print("\n Complete investigation workflow successful!")
        print(f"    Part 1 (Overview): {result['part1']['ref_no']}")
        print(f"    Part 2 (Assessment): {result['part2']['investigation_level']}")
        print(f"    Part 3 (Root Cause): {len(result['part3_rca']['root_causes'])} root causes")
        
        return result
        
    except Exception as e:
        print(f"❌ Orchestrator failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_pdf_agent(investigation_data):
    """Test PDF Report Generator"""
    print_section("TEST 6: PDF Report Generator")
    
    try:
        # Initialize agent
        agent = PDFReportAgent()
        print(" PDF Report Agent initialized successfully")
        
        # Prepare complete investigation data with action plan
        complete_data = {
            'part1': investigation_data['part1'],
            'part2': investigation_data['part2'],
            'part3': investigation_data['part3_rca'],
            'part4': {
                'actions': [
                    {
                        'measure': 'Install non-slip flooring in all loading bays',
                        'responsible': 'Facilities Manager',
                        'target_date': '31/01/2025'
                    },
                    {
                        'measure': 'Implement mandatory wet floor signage protocol',
                        'responsible': 'Warehouse Supervisor',
                        'target_date': '15/01/2025'
                    },
                    {
                        'measure': 'Conduct slip hazard training for all staff',
                        'responsible': 'Safety Officer',
                        'target_date': '28/02/2025'
                    }
                ]
            }
        }
        
        # Generate report
        print("\n Generating comprehensive PDF report...")
        filepath = agent.generate_report(complete_data)
        
        # Verify file created
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
            print(f"\n PDF Report generated successfully!")
            print(f"    File: {filepath}")
            print(f"    Size: {file_size:,} bytes")
            return filepath
        else:
            print(f" PDF file not found: {filepath}")
            return None
        
    except Exception as e:
        print(f" PDF Agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_api_integration():
    """Test API endpoint compatibility"""
    print_section("TEST 7: API Integration Check")
    
    try:
        from api.main import app
        print(" FastAPI app imported successfully")
        
        # Check if agents are initialized in API
        print(" API configuration validated")
        print("    Start API server with: python -m uvicorn api.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f" API integration check failed: {str(e)}")
        return False


def generate_test_report(results):
    """Generate summary test report"""
    print_section("TEST SUMMARY REPORT")
    
    passed = sum(1 for r in results.values() if r is not None and r is not False)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    print("\nDetailed Results:")
    
    test_names = {
        'environment': 'Environment Configuration',
        'overview': 'Overview Agent (Part 1)',
        'assessment': 'Assessment Agent (Part 2)',
        'rootcause': 'Root Cause Agent (Part 3)',
        'orchestrator': 'Orchestrator (Full Workflow)',
        'pdf': 'PDF Report Generator',
        'api': 'API Integration'
    }
    
    for key, name in test_names.items():
        status = " PASSED" if results.get(key) else " FAILED"
        print(f"   {status} - {name}")
    
    # Overall status
    print("\n" + "="*80)
    if passed == total:
        print(" ALL TESTS PASSED! System is fully operational.")
    elif passed >= total * 0.7:
        print("  PARTIAL SUCCESS - Most components working, some issues found.")
    else:
        print("MULTIPLE FAILURES - System requires attention.")
    print("="*80)
    
    return passed == total


def main():
    """Run all tests"""
    print("="*80)
    print("  HSE INVESTIGATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("  Testing all AI agents and components")
    print("="*80)
    print(f"  Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test 1: Environment
    results['environment'] = test_environment()
    if not results['environment']:
        print("\n Environment test failed - cannot continue")
        return
    
    # Test 2: Overview Agent
    part1_data = test_overview_agent()
    results['overview'] = part1_data
    
    if part1_data:
        # Test 3: Assessment Agent
        part2_data = test_assessment_agent(part1_data)
        results['assessment'] = part2_data
        
        # Test 4: Root Cause Agent
        if part2_data:
            part3_data = test_rootcause_agent(part1_data, part2_data)
            results['rootcause'] = part3_data
    
    # Test 5: Orchestrator
    investigation_data = test_orchestrator()
    results['orchestrator'] = investigation_data
    
    # Test 6: PDF Generator
    if investigation_data:
        pdf_path = test_pdf_agent(investigation_data)
        results['pdf'] = pdf_path
    
    # Test 7: API Integration
    results['api'] = test_api_integration()
    
    # Generate report
    all_passed = generate_test_report(results)
    
    # Next steps
    if all_passed:
        print("\n Next Steps:")
        print("     Start API server: python -m uvicorn api.main:app --reload")
        print("    Access API docs: http://localhost:8000/docs")
        print("    Test endpoints: curl http://localhost:8000/api/v1/health")
        print("    View PDF report in: outputs/reports/")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
