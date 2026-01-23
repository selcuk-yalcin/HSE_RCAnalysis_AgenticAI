# Robust JSON Parser Implementation Guide

## 📋 Overview

All AI agents now use a **robust regex-based JSON parser** that eliminates brittle string replacement logic and handles various AI response formats gracefully.

## 🎯 Problem Solved

**Before:**
```python
# Fragile approach - fails with unexpected formats
result = result.replace("```json", "").replace("```", "").strip()
data = json.loads(result)  # ❌ Often crashes
```

**After:**
```python
# Robust approach - handles any format
from .json_parser import safe_json_parse

data = safe_json_parse(
    response_text,
    context="My Agent",
    default={"fallback": "value"}
)  # ✅ Always returns valid dict
```

## 🔧 Core Functions

### 1. `extract_json_from_response(response_text, default=None)`

**Strategy:**
1. Find first `{` and last `}` using regex: `r'\{.*\}'`
2. Extract content between them
3. Parse with `json.loads()`
4. Return default dict if parsing fails

**Handles:**
- ✅ Markdown blocks: ` ```json\n{...}\n``` `
- ✅ Inline JSON: `"Here is data: {...} as requested"`
- ✅ Pure JSON: `{...}`
- ✅ AI reasoning: `"<think>...</think>\n{...}"`
- ✅ Nested objects: `{"a": {"b": {"c": 1}}}`

**Example:**
```python
from agents.json_parser import extract_json_from_response

# Various input formats
inputs = [
    '```json\n{"key": "value"}\n```',
    'AI says: {"result": true} and that\'s it',
    '<think>reasoning here</think>\n{"answer": 42}'
]

for text in inputs:
    data = extract_json_from_response(text)
    print(data)  # Always returns valid dict or {}
```

### 2. `safe_json_parse(response_text, context="", default=None)`

**Enhanced version with:**
- Context-aware error messages
- Debug logging
- Success/failure reporting

**Example:**
```python
from agents.json_parser import safe_json_parse

# With context for better debugging
data = safe_json_parse(
    ai_response,
    context="Assessment Agent - RIDDOR",
    default={"reportable": "N"}
)

# Output:
# 🔍 Parsing JSON from Assessment Agent - RIDDOR...
# ✅ Successfully parsed JSON from Assessment Agent - RIDDOR
```

### 3. `extract_json_array_from_response(response_text, default=None)`

**For array responses:**
- Finds first `[` to last `]`
- Returns list or default list

**Example:**
```python
from agents.json_parser import extract_json_array_from_response

response = "Here are items: [1, 2, 3]"
items = extract_json_array_from_response(response, default=[])
print(items)  # [1, 2, 3]
```

## 🚀 Agent Integration

### AssessmentAgent

**Updated methods:**
1. `_check_riddor()` - RIDDOR reportability check
2. `_determine_investigation_level()` - Investigation level determination

**Before:**
```python
result = result.replace("```json", "").replace("```", "").strip()
try:
    riddor = json.loads(result)
except:
    riddor = {"reportable": "N"}
```

**After:**
```python
riddor = safe_json_parse(
    result,
    context="RIDDOR Assessment",
    default={"reportable": "N", "reason": "Parse failed"}
)
```

### OverviewAgent

**Updated methods:**
1. `_extract_brief_details()` - Extract what/where/when/who

**Before:**
```python
result = result.replace("```json", "").replace("```", "").strip()
json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
details = json.loads(json_match.group(0))
```

**After:**
```python
details = safe_json_parse(
    result,
    context="Brief Details Extraction",
    default={
        "what": description[:200],
        "where": "", "when": "", "who": "",
        "emergency_measures": ""
    }
)
```

### RootCauseAgentV2

**Updated methods:**
1. `_identify_immediate_causes_with_codes()` - A/B category immediate causes
2. `_perform_5why_chain()` - 5-Why analysis chain

**Before:**
```python
result = result.replace("```json", "").replace("```", "").strip()
try:
    data = json.loads(result)
except json.JSONDecodeError:
    return []
```

**After:**
```python
data = safe_json_parse(
    result,
    context="Immediate Causes Identification",
    default={"causes": []}
)

# For 5-Why chains
chain = safe_json_parse(
    result,
    context=f"5-Why Chain for {code}",
    default={"whys": [], "root_cause": {}}
)
```

### ActionPlanAgent

**Updated methods:**
1. `_generate_actions_with_ai()` - AI-powered action plan generation

**Before:**
```python
result_text = result_text.replace("```json", "").replace("```", "").strip()
json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
result = json.loads(json_match.group(0))
```

**After:**
```python
result = safe_json_parse(
    result_text,
    context="Action Plan Generation",
    default=None
)

if result is None or not result:
    return self._generate_fallback_actions()
```

## ✅ Benefits

### 1. **Reliability**
- No more crashes from unexpected AI response formats
- Graceful degradation with sensible defaults

### 2. **Maintainability**
- Single source of truth for JSON parsing logic
- Easy to update parser behavior globally

### 3. **Debugging**
- Context-aware error messages show which agent/operation failed
- Preview of problematic responses for debugging

### 4. **Flexibility**
- Handles new AI model response formats automatically
- Works with reasoning models that include thinking text

## 🧪 Testing

**Test file:** `test_transformation.py`

```bash
# Run tests
cd /Users/selcuk/Desktop/HSE_AgenticAI
python3 -c "
from agents.json_parser import extract_json_from_response

test_cases = [
    '```json\n{\"key\": \"value\"}\n```',
    'Here: {\"a\": 1}',
    '{\"test\": true}',
    'Text {\"nested\": {\"data\": 123}} more',
    'Invalid {broken'
]

for i, tc in enumerate(test_cases, 1):
    result = extract_json_from_response(tc)
    print(f'Test {i}: {result}')
"
```

**Expected output:**
```
Test 1: {'key': 'value'}      ✅
Test 2: {'a': 1}               ✅
Test 3: {'test': True}         ✅
Test 4: {'nested': {'data': 123}} ✅
Test 5: {}                     ✅ (default)
```

## 📝 Usage Guidelines

### When to use `extract_json_from_response()`
- Direct parsing without logging
- Performance-critical paths
- When you want minimal output

### When to use `safe_json_parse()`
- **Recommended for all agent operations**
- When you want debug logging
- When context helps troubleshooting

### Default Values
Always provide meaningful defaults:

```python
# ✅ Good - Meaningful default
data = safe_json_parse(
    response,
    context="RIDDOR Check",
    default={"reportable": "N", "reason": "Parse failed"}
)

# ⚠️ Less good - Empty default
data = safe_json_parse(response, default={})
```

## 🔄 Migration Checklist

For migrating old code:

- [ ] Import `safe_json_parse` from `agents.json_parser`
- [ ] Remove `.replace("```json", "")` logic
- [ ] Remove manual regex extraction
- [ ] Add context string for debugging
- [ ] Provide sensible default values
- [ ] Test with sample AI responses

## 🚀 Deployment

**Status:** ✅ Deployed to Railway (commit: bedae0b)

**Files modified:**
- `agents/json_parser.py` (new)
- `agents/assessment_agent.py`
- `agents/overview_agent.py`
- `agents/rootcause_agent_v2.py`
- `agents/actionplan_agent.py`

**Compatibility:** Backward compatible - existing API contracts maintained

## 🐛 Troubleshooting

### Issue: Parser returns empty dict `{}`

**Cause:** AI response doesn't contain valid JSON

**Debug:**
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

data = safe_json_parse(response, context="Debug")
# Check console for error messages
```

**Check:**
- Print raw AI response before parsing
- Verify AI model is returning JSON
- Check for Unicode/encoding issues

### Issue: Nested objects not extracted

**Cause:** Regex might be too greedy/lazy

**Solution:**
```python
# Use explicit JSON parser if structure is complex
import json
try:
    data = json.loads(response)
except:
    data = extract_json_from_response(response)
```

### Issue: Performance concerns

**Impact:** Minimal - regex is fast for typical responses (<10KB)

**Optimization:**
- Use `extract_json_from_response()` instead of `safe_json_parse()`
- Cache parsed results if same response used multiple times

## 📚 References

- Original implementation: `agents/json_parser.py`
- Test suite: `test_transformation.py`
- Integration examples: See individual agent files
- Deployment: Railway auto-deploy from main branch

---

**Last Updated:** 23 January 2026  
**Version:** 1.0.0  
**Author:** HSE Investigation System Team
