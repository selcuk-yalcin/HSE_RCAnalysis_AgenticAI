"""
Celery inspect helpers (Flower alternative for basic visibility).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def celery_inspect_snapshot(app) -> Dict[str, Any]:
    if app is None:
        return {"error": "celery_not_configured"}
    try:
        insp = app.control.inspect(timeout=2.0)
        if insp is None:
            return {"error": "inspect_unavailable"}
        active = insp.active()
        scheduled = insp.scheduled()
        reserved = insp.reserved()
        stats = insp.stats()
        summary = _build_summary(active, scheduled, reserved, stats)
        return {
            "active": active,
            "scheduled": scheduled,
            "reserved": reserved,
            "stats": stats,
            "summary": summary,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _safe_len(node_map: Optional[Dict[str, Any]]) -> int:
    if not isinstance(node_map, dict):
        return 0
    total = 0
    for _, items in node_map.items():
        if isinstance(items, list):
            total += len(items)
    return total


def _build_summary(active, scheduled, reserved, stats) -> Dict[str, Any]:
    active_count = _safe_len(active)
    reserved_count = _safe_len(reserved)
    scheduled_count = _safe_len(scheduled)
    queue_depth_estimate = reserved_count + scheduled_count
    worker_count = len(stats) if isinstance(stats, dict) else 0

    heartbeat = {}
    if isinstance(stats, dict):
        now = datetime.now(timezone.utc)
        for worker_name, worker_stats in stats.items():
            if not isinstance(worker_stats, dict):
                continue
            ts = worker_stats.get("timestamp")
            lag_sec = None
            if isinstance(ts, (int, float)):
                lag_sec = max(0.0, now.timestamp() - float(ts))
            heartbeat[worker_name] = {
                "clock": worker_stats.get("clock"),
                "timestamp": ts,
                "heartbeat_lag_sec": round(lag_sec, 3) if lag_sec is not None else None,
            }

    return {
        "worker_count": worker_count,
        "active_tasks": active_count,
        "reserved_tasks": reserved_count,
        "scheduled_tasks": scheduled_count,
        "queue_depth_estimate": queue_depth_estimate,
        "heartbeat": heartbeat,
    }
