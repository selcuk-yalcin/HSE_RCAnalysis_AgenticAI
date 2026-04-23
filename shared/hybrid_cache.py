"""
L1 Redis + L2 MongoDB hybrid cache for API-scoped keys (e.g. HITL, derived payloads).
Uses same digest style as redis_client.cache_key with tenant namespace.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

from shared.redis_client import cache_key, get_json as redis_get, set_json as redis_set
from shared.tenant_store import tenant_namespace_prefix

try:
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi

    _PYMONGO = True
except Exception:  # noqa: BLE001
    MongoClient = None  # type: ignore
    ServerApi = None  # type: ignore
    _PYMONGO = False

_mongo_coll = None


def _mongo_collection():
    global _mongo_coll
    if _mongo_coll is not None:
        return _mongo_coll
    if not _PYMONGO:
        return None
    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        return None
    if uri.startswith('"') and uri.endswith('"'):
        uri = uri[1:-1]
    try:
        client = MongoClient(uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db_name = os.getenv("MONGODB_RCA_DB", "rca_database")
        coll_name = os.getenv("MONGODB_HYBRID_CACHE_COLLECTION", "hybrid_api_cache")
        _mongo_coll = client[db_name][coll_name]
        _mongo_coll.create_index("expires_at", expireAfterSeconds=0)
        _mongo_coll.create_index("cache_key", unique=False)
        return _mongo_coll
    except Exception:  # noqa: BLE001
        return None


def namespaced_cache_key(tenant_id: str, prefix: str, payload: Any) -> str:
    base = cache_key(prefix, payload)
    return f"{tenant_namespace_prefix(tenant_id)}:{base}"


def hybrid_get(
    tenant_id: str, prefix: str, payload: Any
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Returns (value, source) where source is 'redis', 'mongodb', or None.
    """
    key = namespaced_cache_key(tenant_id, prefix, payload)
    r = redis_get(key)
    if r is not None:
        return r, "redis"
    coll = _mongo_collection()
    if coll is None:
        return None, None
    try:
        doc = coll.find_one(
            {"cache_key": key, "expires_at": {"$gt": datetime.utcnow()}}
        )
        if doc and doc.get("value") is not None:
            val = doc["value"]
            if isinstance(val, dict):
                redis_set(key, val, int(os.getenv("HYBRID_CACHE_REDIS_TTL", "600")))
                return val, "mongodb"
    except Exception:  # noqa: BLE001
        pass
    return None, None


def hybrid_set(
    tenant_id: str,
    prefix: str,
    payload: Any,
    value: Any,
    ttl_seconds: int = 600,
) -> bool:
    key = namespaced_cache_key(tenant_id, prefix, payload)
    ok = redis_set(key, value, ttl_seconds)
    coll = _mongo_collection()
    if coll is None:
        return ok
    try:
        expires = datetime.utcnow() + timedelta(seconds=max(60, ttl_seconds))
        coll.update_one(
            {"cache_key": key},
            {
                "$set": {
                    "cache_key": key,
                    "tenant_id": tenant_id,
                    "value": value,
                    "expires_at": expires,
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
    except Exception:  # noqa: BLE001
        pass
    return ok
