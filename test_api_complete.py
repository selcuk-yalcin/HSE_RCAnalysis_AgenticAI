"""
Complete API Workflow Test
Tests entire HSG245 investigation from Part 1 to PDF generation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
VERBOSE = True

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_health():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{API_URL}/api/v1/health")
    
    if VERBOSE:
        print(f"GET {API_URL}/api/v1/health")
        print(json.dumps(response.json(), indent=2))
        print()
    
    if response.status_code == 200 and response.json()["status"] == "healthy":
        print_success("Health check passed")
        print_info(f"All agents active: {len(response.json()['agents'])}")
        return True
    else:
        print_error("Health check failed")
        return False

def test_create_incident():
    """Test 2: Create Incident (Part 1)"""
    print_section("TEST 2: Create Incident (Part 1)")
    
    data = {
        "reported_by": "John Smith - Safety Officer",
        "date_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "event_category": "Injury",
        "description": (
            "Warehouse operative slipped on wet floor in loading bay during morning shift. "
            "Employee fell backwards hitting head on concrete floor. "
            "Floor was wet from recent cleaning with no warning signs present. "
            "Employee required hospital treatment for concussion and back pain."
        ),
        "injury_description": "Concussion and back pain requiring hospital treatment",
        "forwarded_to": "Operations Manager, HSE Director"
    }
    
    if VERBOSE:
        print(f"POST {API_URL}/api/v1/incidents/create")
        print("Request:")
        print(json.dumps(data, indent=2))
        print()
    
    response = requests.post(
        f"{API_URL}/api/v1/incidents/create",
        json=data
    )
    
    if VERBOSE:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        print()
    
    if response.status_code == 200:
        result = response.json()
        incident_id = result["data"]["incident_id"]
        incident_type = result["data"]["part1"]["incident_type"]
        
        print_success("Incident created successfully")
        print_info(f"Incident ID: {incident_id}")
        print_info(f"AI Classification: {incident_type}")
        return incident_id
    else:
        print_error("Failed to create incident")
        print(response.text)
        return None

def test_add_assessment(incident_id):
    """Test 3: Add Assessment (Part 2)"""
    print_section("TEST 3: Add Assessment (Part 2)")
    
    data = {
        "incident_id": incident_id,
        "event_type": "Accident",
        "actual_harm": "Serious",
        "riddor_reportable": "Yes"
    }
    
    if VERBOSE:
        print(f"POST {API_URL}/api/v1/incidents/{incident_id}/assessment")
        print("Request:")
        print(json.dumps(data, indent=2))
        print()
    
    print_info("AI analyzing severity... (5-10 seconds)")
    
    response = requests.post(
        f"{API_URL}/api/v1/incidents/{incident_id}/assessment",
        json=data
    )
    
    if VERBOSE:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        print()
    
    if response.status_code == 200:
        result = response.json()
        investigation_level = result["data"]["investigation_level"]
        priority = result["data"]["priority"]
        riddor = result["data"]["riddor_reportable"]
        
        print_success("Assessment completed successfully")
        print_info(f"Investigation Level: {investigation_level}")
        print_info(f"Priority: {priority}")
        print_info(f"RIDDOR: {riddor}")
        return True
    else:
        print_error("Failed to add assessment")
        print(response.text)
        return False

def test_investigate(incident_id):
    """Test 4: Investigation (Part 3)"""
    print_section("TEST 4: Investigation & Root Cause Analysis (Part 3)")
    
    data = {
        "incident_id": incident_id,
        "location": "Warehouse Loading Bay, Area B, 10:30 AM",
        "who_involved": "John Doe, Warehouse Operative, 2 years experience",
        "how_happened": (
            "Employee was carrying boxes from storage to loading dock. "
            "Floor had been mopped 15 minutes prior by cleaning staff. "
            "No wet floor signs were placed. Employee stepped onto wet surface, "
            "lost footing, and fell backwards striking head on concrete floor."
        ),
        "activities": "Loading delivery truck with packaged goods during peak period",
        "working_conditions": (
            "Floor recently cleaned and still wet. No warning signage present. "
            "Normal lighting. No time pressure. Standard PPE worn."
        ),
        "safety_procedures": (
            "Cleaning protocol requires wet floor signs - NOT FOLLOWED. "
            "Loading operations procedure followed normally."
        ),
        "injuries": (
            "Concussion confirmed by hospital. Back pain and bruising. "
            "24-hour observation. 2-week recovery expected. RIDDOR reportable."
        )
    }
    
    if VERBOSE:
        print(f"POST {API_URL}/api/v1/incidents/{incident_id}/investigate")
        print()
    
    print_info("AI performing 5 Why analysis... (10-15 seconds)")
    
    response = requests.post(
        f"{API_URL}/api/v1/incidents/{incident_id}/investigate",
        json=data
    )
    
    if VERBOSE:
        print("\nRoot Cause Analysis Results:")
        result = response.json()
        
        print("\n⚡ Immediate Causes:")
        for cause in result["data"]["immediate_causes"][:3]:
            if isinstance(cause, dict):
                print(f"  • {cause.get('cause', cause)}")
            else:
                print(f"  • {cause}")
        
        print("\n🔧 Underlying Causes:")
        for cause in result["data"]["underlying_causes"][:3]:
            if isinstance(cause, dict):
                print(f"  • {cause.get('cause', cause)}")
            else:
                print(f"  • {cause}")
        
        print("\n🎯 Root Causes:")
        for cause in result["data"]["root_causes"]:
            if isinstance(cause, dict):
                print(f"  • {cause.get('cause', cause)}")
            else:
                print(f"  • {cause}")
        print()
    
    if response.status_code == 200:
        result = response.json()
        immediate_count = len(result["data"]["immediate_causes"])
        underlying_count = len(result["data"]["underlying_causes"])
        root_count = len(result["data"]["root_causes"])
        
        print_success("Root cause analysis completed")
        print_info(f"Immediate: {immediate_count}, Underlying: {underlying_count}, Root: {root_count}")
        return True
    else:
        print_error("Failed to perform investigation")
        print(response.text)
        return False

def test_action_plan(incident_id):
    """Test 5: Generate Action Plan (Part 4)"""
    print_section("TEST 5: Generate Action Plan (Part 4)")
    
    if VERBOSE:
        print(f"POST {API_URL}/api/v1/incidents/{incident_id}/actionplan")
        print()
    
    print_info("AI generating action plan... (5-10 seconds)")
    
    response = requests.post(
        f"{API_URL}/api/v1/incidents/{incident_id}/actionplan"
    )
    
    if VERBOSE:
        print("\nAction Plan:")
        result = response.json()
        
        immediate = [m for m in result["data"]["control_measures"] if m["category"] == "immediate"]
        short_term = [m for m in result["data"]["control_measures"] if m["category"] == "short_term"]
        long_term = [m for m in result["data"]["control_measures"] if m["category"] == "long_term"]
        
        print(f"\n⚡ Immediate Actions ({len(immediate)}):")
        for action in immediate[:2]:
            print(f"  • {action['measure']}")
            print(f"    → {action['responsible']} by {action['target_date']}")
        
        print(f"\n📅 Short-term Actions ({len(short_term)}):")
        for action in short_term[:2]:
            print(f"  • {action['measure']}")
            print(f"    → {action['responsible']} by {action['target_date']}")
        
        print(f"\n🎯 Long-term Actions ({len(long_term)}):")
        for action in long_term[:2]:
            print(f"  • {action['measure']}")
            print(f"    → {action['responsible']} by {action['target_date']}")
        print()
    
    if response.status_code == 200:
        result = response.json()
        total_actions = len(result["data"]["control_measures"])
        
        print_success("Action plan generated successfully")
        print_info(f"Total actions: {total_actions}")
        return True
    else:
        print_error("Failed to generate action plan")
        print(response.text)
        return False

def test_get_incident(incident_id):
    """Test 6: Get Complete Incident"""
    print_section("TEST 6: Get Complete Incident Data")
    
    response = requests.get(f"{API_URL}/api/v1/incidents/{incident_id}")
    
    if response.status_code == 200:
        result = response.json()
        status = result["data"]["status"]
        
        print_success("Retrieved complete incident data")
        print_info(f"Status: {status}")
        
        if status == "completed":
            print_success("Investigation is COMPLETE and ready for PDF generation")
            return True
        else:
            print_error(f"Investigation not complete (status: {status})")
            return False
    else:
        print_error("Failed to retrieve incident")
        return False

def test_generate_pdf(incident_id):
    """Test 7: Generate PDF Report"""
    print_section("TEST 7: Generate PDF Report")
    
    print_info("Generating PDF report...")
    
    response = requests.post(
        f"{API_URL}/api/v1/reports/generate",
        json={"incident_id": incident_id}
    )
    
    if response.status_code == 200:
        filename = f"HSG245_Report_{incident_id}_test.pdf"
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        import os
        file_size = os.path.getsize(filename)
        
        print_success("PDF report generated successfully")
        print_info(f"File: {filename}")
        print_info(f"Size: {file_size:,} bytes")
        
        # Try to open PDF
        try:
            import subprocess
            subprocess.run(['open', filename], check=False)
            print_info("Opening PDF...")
        except:
            pass
        
        return True
    else:
        print_error("Failed to generate PDF")
        print(response.text)
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  HSG245 SMART REPORT - COMPLETE API WORKFLOW TEST")
    print("  Testing Full Investigation Pipeline")
    print("="*80)
    
    start_time = time.time()
    
    # Test 1: Health Check
    if not test_health():
        return
    
    time.sleep(1)
    
    # Test 2: Create Incident
    incident_id = test_create_incident()
    if not incident_id:
        return
    
    time.sleep(1)
    
    # Test 3: Add Assessment
    if not test_add_assessment(incident_id):
        return
    
    time.sleep(1)
    
    # Test 4: Investigation
    if not test_investigate(incident_id):
        return
    
    time.sleep(1)
    
    # Test 5: Action Plan
    if not test_action_plan(incident_id):
        return
    
    time.sleep(1)
    
    # Test 6: Get Complete Incident
    if not test_get_incident(incident_id):
        return
    
    time.sleep(1)
    
    # Test 7: Generate PDF
    if not test_generate_pdf(incident_id):
        return
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print_section("🎉 ALL TESTS PASSED! 🎉")
    
    print("Summary:")
    print("  ✅ Health check")
    print("  ✅ Part 1: Overview - Incident created")
    print("  ✅ Part 2: Assessment - Severity analyzed")
    print("  ✅ Part 3: Investigation - Root causes identified")
    print("  ✅ Part 4: Action plan - Recommendations generated")
    print("  ✅ Get incident - Complete data retrieved")
    print("  ✅ PDF report - Generated successfully")
    print()
    print(f"Incident ID: {incident_id}")
    print(f"Total time: {duration:.1f} seconds")
    print()
    print("="*80)

if __name__ == "__main__":
    main()
