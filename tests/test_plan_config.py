from shared.plan_config import (
    get_plan,
    list_plans,
    monthly_token_budget_for_plan,
    normalize_plan_tier,
)


def test_list_plans_has_three_tiers():
    plans = list_plans()
    assert len(plans) == 3
    ids = {p["id"] for p in plans}
    assert ids == {"starter", "pro", "enterprise"}


def test_normalize_plan_tier_aliases():
    assert normalize_plan_tier("professional") == "pro"
    assert normalize_plan_tier("unknown") == "starter"


def test_monthly_token_budget_mapping():
    assert monthly_token_budget_for_plan("starter") == 220_000
    assert monthly_token_budget_for_plan("pro") == 900_000
    pro = get_plan("pro")
    assert pro["price_monthly"] == 99
