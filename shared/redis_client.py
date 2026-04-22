"""
Redis helper utilities for cache and lightweight state.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Optional

try:
    import redis
except Exception:  # noqa: BLE001
    redis = None


_redis_client = None


def redis_url() -> str:
    return (os.getenv("REDIS_URL") or "redis://localhost:6379/0").strip()


def redis_enabled() -> bool:
    return bool(redis is not None and redis_url())


def get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if redis is None:
        return None
    try:
        _redis_client = redis.from_url(redis_url(), decode_responses=True)
        return _redis_client
    except Exception:  # noqa: BLE001
        return None


def cache_key(prefix: str, payload: Any) -> str:
    dumped = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.sha256(dumped.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def get_json(key: str) -> Optional[dict]:
    client = get_redis_client()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if not raw:
            return None
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        return None


def set_json(key: str, value: Any, ttl_seconds: int = 600) -> bool:
    client = get_redis_client()
    if client is None:
        return False
    try:
        payload = json.dumps(value, ensure_ascii=False, default=str)
        client.setex(key, ttl_seconds, payload)
        return True
    except Exception:  # noqa: BLE001
        return False

