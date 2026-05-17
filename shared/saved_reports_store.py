"""
Per-tenant, per-user saved drafts and completed reports (MongoDB).
Collection: deepwhy_saved_items
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

COLLECTION_NAME = "deepwhy_saved_items"
_MAX_HTML_BYTES = 4_500_000  # ~4.5 MB per artifact field
_indexes_ensured = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_collection() -> Collection:
    global _indexes_ensured
    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured")
    # Atlas: use same cluster as RAG (e.g. mevzuatdb) — DB name often "rca", NOT "analysis_cache".
    db_name = (
        os.getenv("MONGODB_REPORTS_DB")
        or os.getenv("MONGODB_DB")
        or os.getenv("MONGODB_DATABASE")
        or "rca"
    ).strip()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    col = client[db_name][COLLECTION_NAME]
    if not _indexes_ensured:
        col.create_index(
            [("tenant_id", ASCENDING), ("owner_user_id", ASCENDING), ("kind", ASCENDING), ("updated_at", ASCENDING)],
            name="tenant_owner_kind_updated",
        )
        col.create_index(
            [("tenant_id", ASCENDING), ("owner_user_id", ASCENDING), ("incident_id", ASCENDING)],
            unique=True,
            sparse=True,
            name="tenant_owner_incident_unique",
        )
        _indexes_ensured = True
    return col


def _trim_html(value: str) -> str:
    raw = value or ""
    if len(raw.encode("utf-8")) <= _MAX_HTML_BYTES:
        return raw
    return raw.encode("utf-8")[:_MAX_HTML_BYTES].decode("utf-8", errors="ignore")


def _public_doc(doc: dict) -> dict[str, Any]:
    if not doc:
        return {}
    out = {
        "id": str(doc.get("_id") or doc.get("id") or ""),
        "kind": doc.get("kind") or "draft",
        "tenant_id": doc.get("tenant_id") or "",
        "owner_user_id": doc.get("owner_user_id") or "",
        "incident_id": doc.get("incident_id") or "",
        "title": doc.get("title") or "",
        "snapshot": doc.get("snapshot") if isinstance(doc.get("snapshot"), dict) else {},
        "report_ready": bool(doc.get("report_ready")),
        "has_report_html": bool(doc.get("report_html")),
        "has_decision_tree_html": bool(doc.get("decision_tree_html")),
        "analysis_model_preset": doc.get("analysis_model_preset") or "",
        "created_at": doc.get("created_at") or "",
        "updated_at": doc.get("updated_at") or "",
    }
    return out


def store_location() -> dict[str, str]:
    """Where reports are persisted (for health checks / ops)."""
    uri = (os.getenv("MONGODB_URI") or "").strip()
    db_name = (
        os.getenv("MONGODB_REPORTS_DB")
        or os.getenv("MONGODB_DB")
        or os.getenv("MONGODB_DATABASE")
        or "rca"
    ).strip()
    return {
        "configured": bool(uri),
        "database": db_name,
        "collection": COLLECTION_NAME,
        "note": "User reports are NOT stored in analysis_cache (that is RCA pipeline cache).",
    }


def ping_store() -> tuple[bool, str]:
    try:
        col = _get_collection()
        col.database.client.admin.command("ping")
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def count_all_documents() -> int:
    try:
        return _get_collection().count_documents({})
    except Exception:  # noqa: BLE001
        return -1


def ensure_collection() -> dict[str, Any]:
    """Create collection + indexes on deploy (empty collection becomes visible in Atlas)."""
    col = _get_collection()
    n = col.estimated_document_count()
    info = store_location()
    info["document_count"] = n
    info["ready"] = True
    return info


def list_items(tenant_id: str, owner_user_id: str, *, kind: Optional[str] = None) -> list[dict[str, Any]]:
    col = _get_collection()
    query: dict[str, Any] = {"tenant_id": tenant_id, "owner_user_id": owner_user_id}
    if kind in ("draft", "report"):
        query["kind"] = kind
    cursor = col.find(query, projection={"report_html": 0, "decision_tree_html": 0}).sort("updated_at", -1).limit(100)
    return [_public_doc(d) for d in cursor]


def get_item(tenant_id: str, owner_user_id: str, item_id: str) -> Optional[dict[str, Any]]:
    col = _get_collection()
    doc = col.find_one({"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id})
    if not doc:
        return None
    return _public_doc(doc)


def get_item_full(tenant_id: str, owner_user_id: str, item_id: str) -> Optional[dict[str, Any]]:
    col = _get_collection()
    return col.find_one({"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id})


def get_artifact_html(
    tenant_id: str,
    owner_user_id: str,
    item_id: str,
    artifact: str,
) -> Optional[str]:
    doc = get_item_full(tenant_id, owner_user_id, item_id)
    if not doc:
        return None
    if artifact == "decision_tree":
        return doc.get("decision_tree_html") or ""
    return doc.get("report_html") or ""


def delete_item(tenant_id: str, owner_user_id: str, item_id: str) -> bool:
    col = _get_collection()
    res = col.delete_one({"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id})
    return res.deleted_count > 0


def _build_title(snapshot: dict, title_hint: str = "", incident_id: str = "") -> str:
    if title_hint:
        return title_hint[:96]
    hint = f"{snapshot.get('location') or ''} {snapshot.get('reportedBy') or ''}".strip()
    if hint:
        return hint[:96]
    if incident_id:
        return incident_id[:96]
    return "Kayıt"


def upsert_item(
    *,
    tenant_id: str,
    owner_user_id: str,
    kind: str,
    snapshot: dict,
    title_hint: str = "",
    incident_id: str = "",
    report_ready: bool = False,
    analysis_model_preset: str = "",
    item_id: Optional[str] = None,
) -> dict[str, Any]:
    col = _get_collection()
    now = _utc_now_iso()
    kind_norm = "report" if kind == "report" else "draft"

    if kind_norm == "report" and incident_id:
        item_id = f"report-{incident_id}"
    elif not item_id:
        item_id = str(uuid.uuid4())

    existing = col.find_one({"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id})
    title = _build_title(snapshot or {}, title_hint, incident_id)
    merged_snapshot = {**(existing.get("snapshot") if existing else {}), **(snapshot or {})}

    doc = {
        "_id": item_id,
        "tenant_id": tenant_id,
        "owner_user_id": owner_user_id,
        "kind": kind_norm,
        "incident_id": incident_id or (existing or {}).get("incident_id") or "",
        "title": title,
        "snapshot": merged_snapshot,
        "report_ready": report_ready if kind_norm == "report" else bool((existing or {}).get("report_ready")),
        "analysis_model_preset": analysis_model_preset or (existing or {}).get("analysis_model_preset") or "",
        "updated_at": now,
    }
    if not existing:
        doc["created_at"] = now
    else:
        doc["created_at"] = existing.get("created_at") or now
        if existing.get("report_html"):
            doc["report_html"] = existing["report_html"]
        if existing.get("decision_tree_html"):
            doc["decision_tree_html"] = existing["decision_tree_html"]

    try:
        col.replace_one(
            {"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id},
            doc,
            upsert=True,
        )
    except DuplicateKeyError:
        # incident_id unique collision — update existing report row
        if incident_id:
            col.update_one(
                {
                    "tenant_id": tenant_id,
                    "owner_user_id": owner_user_id,
                    "incident_id": incident_id,
                },
                {"$set": {k: v for k, v in doc.items() if k != "_id"}},
            )
            found = col.find_one(
                {"tenant_id": tenant_id, "owner_user_id": owner_user_id, "incident_id": incident_id}
            )
            return _public_doc(found or doc)
        raise

    saved = col.find_one({"_id": item_id})
    return _public_doc(saved or doc)


def attach_artifacts(
    *,
    tenant_id: str,
    owner_user_id: str,
    item_id: str,
    report_html: str,
    decision_tree_html: str,
) -> Optional[dict[str, Any]]:
    col = _get_collection()
    now = _utc_now_iso()
    res = col.update_one(
        {"_id": item_id, "tenant_id": tenant_id, "owner_user_id": owner_user_id},
        {
            "$set": {
                "report_html": _trim_html(report_html),
                "decision_tree_html": _trim_html(decision_tree_html),
                "report_ready": True,
                "kind": "report",
                "updated_at": now,
            }
        },
    )
    if res.matched_count == 0:
        return None
    return _public_doc(col.find_one({"_id": item_id}))
