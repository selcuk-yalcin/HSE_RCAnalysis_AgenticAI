from agents.actionplan_agent import ActionPlanAgent


def _agent():
    # Bypass network-heavy __init__; parser/validator methods are pure.
    return ActionPlanAgent.__new__(ActionPlanAgent)


def test_sanitized_parser_handles_markdown_and_trailing_commas():
    agent = _agent()
    malformed = """```json
{
  "control_measures": [
    {
      "measure": "LOTO lock installation",
      "responsible": "Safety Manager",
      "target_date": "01/05/2026",
      "category": "immediate",
      "control_type": "engineering",
    }
  ],
  "immediate": ["Install locks"],
  "short_term": ["Update SOP"],
  "long_term": ["Audit system"],
  "responsible": {"Install locks": "Safety Manager"},
  "deadlines": {"Install locks": "01/05/2026"},
}
```"""
    parsed, info = agent._parse_action_plan_response(malformed)
    assert isinstance(parsed, dict)
    assert info["sanitized"] is True
    assert parsed["control_measures"][0]["category"] == "immediate"


def test_schema_validator_rejects_missing_required_keys():
    agent = _agent()
    payload = {
        "control_measures": [],
        "immediate": [],
        "short_term": [],
        # long_term intentionally missing
        "responsible": {},
        "deadlines": {},
    }
    assert agent._validate_action_plan_schema(payload) is False


def test_parser_returns_error_on_truncated_json():
    agent = _agent()
    truncated = '{"control_measures": [{"measure": "A"}], "immediate": ['
    parsed, info = agent._parse_action_plan_response(truncated)
    assert parsed is None
    assert isinstance(info.get("error"), str) and info["error"]

