"""
P0.11 — Central pricing plan configuration (single source for UI + token accounts).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_PLANS_PATH = Path(__file__).resolve().parent / "pricing_plans.json"

VALID_PLAN_IDS = ("starter", "pro", "enterprise")


@lru_cache(maxsize=1)
def load_pricing_catalog() -> Dict[str, Any]:
    with open(_PLANS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def list_plans() -> List[Dict[str, Any]]:
    return list(load_pricing_catalog().get("plans") or [])


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    pid = (plan_id or "").strip().lower()
    for plan in list_plans():
        if (plan.get("id") or "").lower() == pid:
            return dict(plan)
    return None


def normalize_plan_tier(plan_id: str) -> str:
    pid = (plan_id or "starter").strip().lower()
    if pid in VALID_PLAN_IDS:
        return pid
    aliases = {"professional": "pro", "enterprise": "enterprise", "starter": "starter"}
    return aliases.get(pid, "starter")


def monthly_token_budget_for_plan(plan_id: str) -> int:
    plan = get_plan(normalize_plan_tier(plan_id))
    if plan:
        return max(1000, int(plan.get("monthly_token_budget") or 220_000))
    return 220_000


def monthly_report_quota_for_plan(plan_id: str) -> int:
    plan = get_plan(normalize_plan_tier(plan_id))
    if plan:
        return max(1, int(plan.get("monthly_report_quota") or 10))
    return 10
