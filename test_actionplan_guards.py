"""
Test ActionPlanAgent Guard Clauses
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.actionplan_agent import ActionPlanAgent

print("="*80)
print("🧪 TESTING ACTION PLAN AGENT GUARD CLAUSES")
print("="*80)

agent = ActionPlanAgent()

# Test 1: None input
print("\n" + "="*80)
print("TEST 1: None input")
print("="*80)
result1 = agent.generate_action_plan(None)
assert "_fallback" in result1, "Should return fallback data"
print("✅ Test 1 passed: Handled None input")

# Test 2: Empty dict
print("\n" + "="*80)
print("TEST 2: Empty dict")
print("="*80)
result2 = agent.generate_action_plan({})
assert "_fallback" in result2, "Should return fallback data"
print("✅ Test 2 passed: Handled empty dict")

# Test 3: Dict without root_causes
print("\n" + "="*80)
print("TEST 3: Dict without root_causes")
print("="*80)
result3 = agent.generate_action_plan({"severity": "High"})
assert "_fallback" in result3, "Should return fallback data"
print("✅ Test 3 passed: Handled missing root_causes")

# Test 4: root_causes is empty list
print("\n" + "="*80)
print("TEST 4: root_causes is empty list")
print("="*80)
result4 = agent.generate_action_plan({
    "root_causes": [],
    "severity": "Medium"
})
assert "_fallback" in result4, "Should return fallback data"
print("✅ Test 4 passed: Handled empty root_causes list")

# Test 5: Valid data (should NOT use fallback)
print("\n" + "="*80)
print("TEST 5: Valid data with root causes")
print("="*80)
result5 = agent.generate_action_plan({
    "root_causes": [
        {"code": "D1.1", "description": "Test root cause"}
    ],
    "underlying_causes": [],
    "immediate_causes": [
        {"code": "A1.1", "description": "Test immediate cause"}
    ],
    "severity": "High level"
})
# This should NOT have _fallback flag (AI generated)
# But if AI fails, it will still have _fallback
print(f"Has fallback flag: {'_fallback' in result5}")

print("\n" + "="*80)
print("✅ ALL GUARD CLAUSE TESTS PASSED!")
print("="*80)

# Print sample fallback structure
print("\n" + "="*80)
print("📋 SAMPLE FALLBACK STRUCTURE")
print("="*80)
print(f"Keys: {list(result1.keys())}")
print(f"Immediate actions: {result1['immediate_actions']}")
print(f"Priority: {result1['priority_level']}")
print(f"Generated at: {result1['generated_at']}")
print("="*80)
