"""
Celery inspect helpers (Flower alternative for basic visibility).
"""

from __future__ import annotations

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
        return {
            "active": active,
            "scheduled": scheduled,
            "reserved": reserved,
            "stats": stats,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
