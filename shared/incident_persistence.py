"""
Cross-process incident record merge (API + Celery worker) via Redis.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from shared.redis_client import get_redis_client


def incident_redis_key(tenant_id: str, incident_id: str) -> str:
    return f"hse:incident:{tenant_id}:{incident_id}"


def _ttl_seconds() -> int:
    raw = (os.getenv("INCIDENT_REDIS_TTL_SECONDS") or "2592000").strip()
    try:
        return max(3600, int(raw))
    except ValueError:
        return 2592000


def load_incident_from_redis(tenant_id: str, incident_id: str) -> Optional[dict[str, Any]]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(incident_redis_key(tenant_id, incident_id))
        if not raw:
            return None
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:  # noqa: BLE001
        return None


def merge_incident_fields(
    tenant_id: str,
    incident_id: str,
    patch: dict[str, Any],
    *,
    ttl_seconds: Optional[int] = None,
) -> bool:
    """
    Merge fields into the Redis incident blob (create minimal shell if missing).
    Returns True when Redis write succeeded.
    """
    if not tenant_id or not incident_id or not patch:
        return False
    client = get_redis_client()
    if client is None:
        return False
    key = incident_redis_key(tenant_id, incident_id)
    try:
        existing = load_incident_from_redis(tenant_id, incident_id) or {}
        if not isinstance(existing, dict):
            existing = {}
        if not existing.get("id"):
            existing["id"] = incident_id
        if not existing.get("tenant_id"):
            existing["tenant_id"] = tenant_id
        for k, v in patch.items():
            if v is not None:
                existing[k] = v
        client.setex(
            key,
            ttl_seconds if ttl_seconds is not None else _ttl_seconds(),
            json.dumps(existing, ensure_ascii=False, default=str),
        )
        return True
    except Exception:  # noqa: BLE001
        return False
