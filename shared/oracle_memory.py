"""
Oracle-style long-lived context per tenant (MongoDB).
Injected into investigation payloads as oracle_context.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi

    _PYMONGO = True
except Exception:  # noqa: BLE001
    MongoClient = None  # type: ignore
    _PYMONGO = False

_collection = None


def _coll():
    global _collection
    if _collection is not None:
        return _collection
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
        name = os.getenv("MONGODB_ORACLE_COLLECTION", "oracle_context")
        _collection = client[db_name][name]
        _collection.create_index([("tenant_id", 1), ("updated_at", -1)])
        return _collection
    except Exception:  # noqa: BLE001
        return None


def merge_oracle_into_investigation(
    tenant_id: str, investigation: Dict[str, Any]
) -> Dict[str, Any]:
    """Append stored oracle summary into investigation dict for agents."""
    text = get_latest_context_text(tenant_id)
    if not text:
        return investigation
    out = dict(investigation)
    prev = (out.get("oracle_context") or "").strip()
    out["oracle_context"] = (prev + "\n\n" + text).strip() if prev else text
    return out


def get_latest_context_text(tenant_id: str) -> str:
    coll = _coll()
    if coll is None:
        return ""
    try:
        doc = coll.find_one({"tenant_id": tenant_id}, sort=[("updated_at", -1)])
        if doc and doc.get("summary"):
            return str(doc["summary"])
    except Exception:  # noqa: BLE001
        pass
    return ""


def upsert_context(
    tenant_id: str,
    summary: str,
    incident_id: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    coll = _coll()
    if coll is None:
        return False
    try:
        coll.insert_one(
            {
                "tenant_id": tenant_id,
                "incident_id": incident_id or None,
                "summary": summary,
                "metadata": metadata or {},
                "updated_at": datetime.utcnow(),
            }
        )
        return True
    except Exception:  # noqa: BLE001
        return False


def list_recent(tenant_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    coll = _coll()
    if coll is None:
        return []
    try:
        cur = (
            coll.find({"tenant_id": tenant_id})
            .sort("updated_at", -1)
            .limit(limit)
        )
        return [
            {
                "summary": d.get("summary"),
                "incident_id": d.get("incident_id"),
                "updated_at": d.get("updated_at"),
            }
            for d in cur
        ]
    except Exception:  # noqa: BLE001
        return []
