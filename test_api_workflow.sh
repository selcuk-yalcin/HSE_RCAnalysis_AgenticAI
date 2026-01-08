#!/bin/bash

# HSG245 Smart Report - Complete API Workflow Test
# Tests all endpoints from Part 1 to PDF generation

echo "========================================================================"
echo "  HSG245 SMART REPORT - COMPLETE API WORKFLOW TEST"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API Base URL
API_URL="http://localhost:8000"

# Test 1: Health Check
echo -e "${BLUE}TEST 1: Health Check${NC}"
echo "GET $API_URL/api/v1/health"
echo ""
HEALTH=$(curl -s "$API_URL/api/v1/health")
echo "$HEALTH" | python -m json.tool
echo ""

if echo "$HEALTH" | grep -q '"status": "healthy"'; then
    echo -e "${GREEN}✅ Health check PASSED${NC}"
else
    echo -e "${RED}❌ Health check FAILED${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 2: Create Incident (Part 1)
echo -e "${BLUE}TEST 2: Create Incident (Part 1)${NC}"
echo "POST $API_URL/api/v1/incidents/create"
echo ""

PART1_DATA='{
  "reported_by": "John Smith - Safety Officer",
  "date_time": "2026-01-05T10:30:00",
  "event_category": "Injury",
  "brief_details": "Warehouse operative slipped on wet floor in loading bay during morning shift. Employee fell backwards hitting head on concrete floor. Floor was wet from recent cleaning with no warning signs present. Employee required hospital treatment for concussion and back pain.",
  "forwarded_to": "Operations Manager, HSE Director"
}'

echo -e "${YELLOW}Request:${NC}"
echo "$PART1_DATA" | python -m json.tool
echo ""

PART1_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/incidents/create" \
  -H "Content-Type: application/json" \
  -d "$PART1_DATA")

echo -e "${YELLOW}Response:${NC}"
echo "$PART1_RESPONSE" | python -m json.tool
echo ""

# Extract incident ID
INCIDENT_ID=$(echo "$PART1_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['data']['incident_id'])" 2>/dev/null)

if [ -z "$INCIDENT_ID" ]; then
    echo -e "${RED}❌ Failed to create incident${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Incident created successfully${NC}"
    echo -e "${GREEN}   Incident ID: $INCIDENT_ID${NC}"
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Wait for user
read -p "Press Enter to continue to Part 2..."
echo ""

# Test 3: Add Assessment (Part 2)
echo -e "${BLUE}TEST 3: Add Assessment (Part 2)${NC}"
echo "POST $API_URL/api/v1/incidents/$INCIDENT_ID/assessment"
echo ""

PART2_DATA="{
  \"incident_id\": \"$INCIDENT_ID\",
  \"event_type\": \"Accident\",
  \"actual_harm\": \"Serious\",
  \"riddor_reportable\": \"Yes\"
}"

echo -e "${YELLOW}Request:${NC}"
echo "$PART2_DATA" | python -m json.tool
echo ""

PART2_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/incidents/$INCIDENT_ID/assessment" \
  -H "Content-Type: application/json" \
  -d "$PART2_DATA")

echo -e "${YELLOW}Response:${NC}"
echo "$PART2_RESPONSE" | python -m json.tool
echo ""

if echo "$PART2_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✅ Assessment completed successfully${NC}"
else
    echo -e "${RED}❌ Assessment failed${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Wait for user
read -p "Press Enter to continue to Part 3..."
echo ""

# Test 4: Investigation (Part 3)
echo -e "${BLUE}TEST 4: Investigation & Root Cause Analysis (Part 3)${NC}"
echo "POST $API_URL/api/v1/incidents/$INCIDENT_ID/investigate"
echo ""

PART3_DATA="{
  \"incident_id\": \"$INCIDENT_ID\",
  \"location\": \"Warehouse Loading Bay, Area B, 10:30 AM\",
  \"who_involved\": \"John Doe, Warehouse Operative, 2 years experience, authorized to operate in loading area\",
  \"how_happened\": \"Employee was carrying boxes from storage to loading dock. Floor had been mopped 15 minutes prior by cleaning staff. No wet floor signs were placed. Employee stepped onto wet surface, lost footing, and fell backwards striking head on concrete floor. Boxes scattered across floor creating additional hazard.\",
  \"activities\": \"Loading delivery truck with packaged goods for customer shipment. Normal morning operations during peak loading period.\",
  \"working_conditions\": \"Floor recently cleaned and still wet. No warning signage present. Normal lighting conditions. No time pressure reported. Standard PPE worn (safety shoes, hi-vis vest).\",
  \"safety_procedures\": \"Cleaning protocol requires wet floor signs to be placed - this was not followed. Standard operating procedure for loading operations was being followed. No deviation from normal work methods reported.\",
  \"injuries\": \"Concussion confirmed by hospital. Back pain and bruising. Employee kept for 24-hour observation. Expected 2-week recovery period. RIDDOR reportable injury.\"
}"

echo -e "${YELLOW}Request:${NC}"
echo "$PART3_DATA" | python -m json.tool
echo ""

echo -e "${YELLOW}AI is analyzing (this may take 10-15 seconds)...${NC}"
echo ""

PART3_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/incidents/$INCIDENT_ID/investigate" \
  -H "Content-Type: application/json" \
  -d "$PART3_DATA")

echo -e "${YELLOW}Response:${NC}"
echo "$PART3_RESPONSE" | python -m json.tool
echo ""

if echo "$PART3_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✅ Root cause analysis completed successfully${NC}"
else
    echo -e "${RED}❌ Investigation failed${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Wait for user
read -p "Press Enter to continue to Part 4..."
echo ""

# Test 5: Generate Action Plan (Part 4)
echo -e "${BLUE}TEST 5: Generate Action Plan (Part 4)${NC}"
echo "POST $API_URL/api/v1/incidents/$INCIDENT_ID/actionplan"
echo ""

echo -e "${YELLOW}AI is generating action plan (this may take 5-10 seconds)...${NC}"
echo ""

PART4_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/incidents/$INCIDENT_ID/actionplan" \
  -H "Content-Type: application/json")

echo -e "${YELLOW}Response:${NC}"
echo "$PART4_RESPONSE" | python -m json.tool
echo ""

if echo "$PART4_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✅ Action plan generated successfully${NC}"
else
    echo -e "${RED}❌ Action plan generation failed${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 6: Get Complete Incident
echo -e "${BLUE}TEST 6: Get Complete Incident Data${NC}"
echo "GET $API_URL/api/v1/incidents/$INCIDENT_ID"
echo ""

COMPLETE_RESPONSE=$(curl -s "$API_URL/api/v1/incidents/$INCIDENT_ID")

echo -e "${YELLOW}Complete Investigation Data:${NC}"
echo "$COMPLETE_RESPONSE" | python -m json.tool
echo ""

if echo "$COMPLETE_RESPONSE" | grep -q '"status": "completed"'; then
    echo -e "${GREEN}✅ Investigation is complete and ready for PDF${NC}"
else
    echo -e "${RED}❌ Investigation not completed${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Wait for user
read -p "Press Enter to generate PDF report..."
echo ""

# Test 7: Generate PDF Report
echo -e "${BLUE}TEST 7: Generate PDF Report${NC}"
echo "POST $API_URL/api/v1/reports/generate"
echo ""

PDF_FILENAME="HSG245_Report_${INCIDENT_ID}_test.pdf"

curl -s -X POST "$API_URL/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -d "{\"incident_id\": \"$INCIDENT_ID\"}" \
  -o "$PDF_FILENAME"

if [ -f "$PDF_FILENAME" ]; then
    FILE_SIZE=$(ls -lh "$PDF_FILENAME" | awk '{print $5}')
    echo -e "${GREEN}✅ PDF report generated successfully${NC}"
    echo -e "${GREEN}   File: $PDF_FILENAME${NC}"
    echo -e "${GREEN}   Size: $FILE_SIZE${NC}"
    echo ""
    echo -e "${YELLOW}Opening PDF...${NC}"
    open "$PDF_FILENAME" 2>/dev/null || echo "PDF saved to: $(pwd)/$PDF_FILENAME"
else
    echo -e "${RED}❌ PDF generation failed${NC}"
    exit 1
fi
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Test 8: List All Incidents
echo -e "${BLUE}TEST 8: List All Incidents${NC}"
echo "GET $API_URL/api/v1/incidents"
echo ""

INCIDENTS_LIST=$(curl -s "$API_URL/api/v1/incidents")

echo -e "${YELLOW}All Incidents:${NC}"
echo "$INCIDENTS_LIST" | python -m json.tool
echo ""

INCIDENTS_COUNT=$(echo "$INCIDENTS_LIST" | python -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null)

echo -e "${GREEN}✅ Total incidents in system: $INCIDENTS_COUNT${NC}"
echo ""
echo "------------------------------------------------------------------------"
echo ""

# Summary
echo "========================================================================"
echo -e "${GREEN}  🎉 ALL TESTS PASSED! 🎉${NC}"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  ✅ Health check"
echo "  ✅ Part 1: Overview - Incident created"
echo "  ✅ Part 2: Assessment - Severity analyzed"
echo "  ✅ Part 3: Investigation - Root causes identified"
echo "  ✅ Part 4: Action plan - Recommendations generated"
echo "  ✅ Get incident - Complete data retrieved"
echo "  ✅ PDF report - Generated successfully"
echo "  ✅ List incidents - System working"
echo ""
echo "Incident ID: $INCIDENT_ID"
echo "PDF Report: $PDF_FILENAME"
echo ""
echo "========================================================================"
echo ""
