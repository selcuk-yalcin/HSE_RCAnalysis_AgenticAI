"""
Lightweight pattern aggregation over in-memory incident payloads (per-tenant).
For deeper analytics, plug a warehouse / BI tool later.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


def aggregate_root_cause_codes(incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    codes: Counter[str] = Counter()
    for inc in incidents:
        part3 = inc.get("part3") or {}
        for rc in part3.get("root_causes") or []:
            c = (rc.get("code") or "").strip()
            if c:
                codes[c] += 1
    top = codes.most_common(25)
    return {
        "unique_codes": len(codes),
        "total_root_cause_entries": sum(codes.values()),
        "top_codes": [{"code": k, "count": v} for k, v in top],
    }


def summarize_status(incidents: List[Dict[str, Any]]) -> Dict[str, int]:
    st: Counter[str] = Counter()
    for inc in incidents:
        st[str(inc.get("status") or "unknown")] += 1
    return dict(st)
