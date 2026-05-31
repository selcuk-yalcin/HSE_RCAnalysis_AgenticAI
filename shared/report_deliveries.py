"""
Report completion email deliveries with idempotency (P0.10).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from shared.email_sender import send_email
from shared.report_delivery_email import build_report_ready_email, normalize_delivery_lang
from shared.signed_links import sign_payload

COLLECTION_NAME = "report_deliveries"
_indexes_ensured = False
_mem_deliveries: dict[str, dict[str, Any]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mongo_enabled() -> bool:
    return bool((os.getenv("MONGODB_URI") or "").strip())


def _get_collection() -> Collection:
    global _indexes_ensured
    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured")
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
            [("delivery_key", ASCENDING)],
            unique=True,
            name="delivery_key_unique",
        )
        col.create_index(
            [("tenant_id", ASCENDING), ("owner_user_id", ASCENDING), ("created_at", DESCENDING)],
            name="tenant_owner_created",
        )
        _indexes_ensured = True
    return col


def notify_enabled_for_user(*, tenant_id: str, user_prefs: Optional[dict] = None) -> bool:
    tenant_default = (os.getenv("REPORT_NOTIFY_EMAIL_DEFAULT") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )
    if isinstance(user_prefs, dict) and "notify_report_ready_email" in user_prefs:
        return bool(user_prefs.get("notify_report_ready_email"))
    return tenant_default


def build_delivery_key(
    *,
    report_id: str,
    owner_user_id: str,
    artifact_version: str = "v1",
) -> str:
    return f"{report_id}|{owner_user_id}|{artifact_version}"


def _public_doc(doc: dict) -> dict[str, Any]:
    return {
        "id": str(doc.get("_id") or doc.get("id") or ""),
        "delivery_key": doc.get("delivery_key") or "",
        "report_id": doc.get("report_id") or "",
        "tenant_id": doc.get("tenant_id") or "",
        "owner_user_id": doc.get("owner_user_id") or "",
        "recipient_email": doc.get("recipient_email") or "",
        "channel": doc.get("channel") or "email",
        "status": doc.get("status") or "pending",
        "attempt_count": int(doc.get("attempt_count") or 0),
        "last_error": doc.get("last_error") or "",
        "provider_message_id": doc.get("provider_message_id") or "",
        "sent_at": doc.get("sent_at") or "",
        "created_at": doc.get("created_at") or "",
        "updated_at": doc.get("updated_at") or "",
    }


def list_deliveries(tenant_id: str, owner_user_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    limit = max(1, min(100, int(limit)))
    if _mongo_enabled():
        col = _get_collection()
        cursor = (
            col.find({"tenant_id": tenant_id, "owner_user_id": owner_user_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return [_public_doc(d) for d in cursor]
    rows = [
        d
        for d in _mem_deliveries.values()
        if d.get("tenant_id") == tenant_id and d.get("owner_user_id") == owner_user_id
    ]
    rows.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return [_public_doc(d) for d in rows[:limit]]


def enqueue_report_ready_email(
    *,
    tenant_id: str,
    owner_user_id: str,
    recipient_email: str,
    report_id: str,
    incident_id: str,
    artifact_version: str = "v1",
    user_prefs: Optional[dict] = None,
    output_language: str = "tr",
    html_path: str = "",
    docx_path: str = "",
    library_item_id: str = "",
) -> Optional[dict[str, Any]]:
    """Create pending delivery row and schedule Celery task when available."""
    if not notify_enabled_for_user(tenant_id=tenant_id, user_prefs=user_prefs):
        return None
    email = (recipient_email or "").strip().lower()
    if not email or "@" not in email:
        return None

    delivery_key = build_delivery_key(
        report_id=report_id,
        owner_user_id=owner_user_id,
        artifact_version=artifact_version,
    )
    now = _utc_now_iso()
    doc = {
        "delivery_key": delivery_key,
        "report_id": report_id,
        "incident_id": incident_id,
        "tenant_id": tenant_id,
        "owner_user_id": owner_user_id,
        "recipient_email": email,
        "channel": "email",
        "status": "pending",
        "attempt_count": 0,
        "last_error": "",
        "provider_message_id": "",
        "sent_at": "",
        "artifact_version": artifact_version,
        "output_language": normalize_delivery_lang(output_language),
        "html_path": (html_path or "").strip(),
        "docx_path": (docx_path or "").strip(),
        "library_item_id": (library_item_id or "").strip(),
        "created_at": now,
        "updated_at": now,
    }

    if _mongo_enabled():
        col = _get_collection()
        existing = col.find_one({"delivery_key": delivery_key})
        if existing and existing.get("status") == "sent":
            return _public_doc(existing)
        try:
            col.insert_one(doc)
        except DuplicateKeyError:
            existing = col.find_one({"delivery_key": delivery_key})
            if existing:
                doc = existing
    else:
        if delivery_key in _mem_deliveries and _mem_deliveries[delivery_key].get("status") == "sent":
            return _public_doc(_mem_deliveries[delivery_key])
        _mem_deliveries[delivery_key] = doc

    try:
        from tasks.report_delivery_tasks import send_report_delivery_email

        send_report_delivery_email.delay(delivery_key)
    except Exception:
        # Synchronous fallback for dev without worker
        process_delivery(delivery_key)

    return _public_doc(doc)


def _load_by_key(delivery_key: str) -> Optional[dict]:
    if _mongo_enabled():
        return _get_collection().find_one({"delivery_key": delivery_key})
    return _mem_deliveries.get(delivery_key)


def _save_doc(doc: dict) -> None:
    delivery_key = doc.get("delivery_key") or ""
    if _mongo_enabled():
        col = _get_collection()
        col.update_one({"delivery_key": delivery_key}, {"$set": doc}, upsert=True)
    else:
        _mem_deliveries[delivery_key] = doc


def _load_report_html_bytes(doc: dict) -> tuple[bytes, str]:
    """Load HTML report bytes for email attachment. Returns (payload, filename)."""
    incident_id = (doc.get("incident_id") or "report").strip()
    filename = f"{incident_id}_report.html"
    max_bytes = int((os.getenv("REPORT_EMAIL_MAX_ATTACHMENT_BYTES") or "8388608").strip() or "8388608")

    html_path = (doc.get("html_path") or "").strip()
    if html_path:
        path = Path(html_path)
        if path.is_file():
            raw = path.read_bytes()
            if len(raw) <= max_bytes:
                return raw, filename

    library_item_id = (doc.get("library_item_id") or doc.get("report_id") or "").strip()
    tenant_id = doc.get("tenant_id") or ""
    owner_user_id = doc.get("owner_user_id") or ""
    if library_item_id and tenant_id and owner_user_id:
        try:
            from shared import saved_reports_store

            html = saved_reports_store.get_artifact_html(
                tenant_id, owner_user_id, library_item_id, "report"
            )
            if html:
                raw = html.encode("utf-8")
                if len(raw) <= max_bytes:
                    return raw, filename
        except Exception:
            pass

    return b"", filename


def process_delivery(delivery_key: str) -> dict[str, Any]:
    """Send localized email with HTML attachment; idempotent when already sent."""
    doc = _load_by_key(delivery_key)
    if not doc:
        return {"ok": False, "error": "not_found"}

    if doc.get("status") == "sent":
        return {"ok": True, "skipped": "already_sent"}

    max_attempts = int((os.getenv("REPORT_DELIVERY_MAX_ATTEMPTS") or "3").strip() or "3")
    attempt = int(doc.get("attempt_count") or 0) + 1
    doc["attempt_count"] = attempt
    doc["updated_at"] = _utc_now_iso()

    base_url = (
        os.getenv("REPORT_DELIVERY_API_BASE")
        or os.getenv("BACKEND_PUBLIC_URL")
        or os.getenv("PUBLIC_API_URL")
        or os.getenv("PUBLIC_APP_URL")
        or os.getenv("APP_BASE_URL")
        or "https://cpanel.inferaworld.com"
    ).rstrip("/")
    ttl = int((os.getenv("REPORT_LINK_TTL_SECONDS") or "86400").strip() or "86400")
    tenant_id = doc.get("tenant_id") or ""
    owner_user_id = doc.get("owner_user_id") or ""
    incident_id = doc.get("incident_id") or ""
    report_id = doc.get("report_id") or ""

    html_token = sign_payload(
        {
            "tenant_id": tenant_id,
            "owner_user_id": owner_user_id,
            "incident_id": incident_id,
            "artifact": "html",
        },
        ttl_seconds=ttl,
    )
    docx_token = sign_payload(
        {
            "tenant_id": tenant_id,
            "owner_user_id": owner_user_id,
            "incident_id": incident_id,
            "artifact": "docx",
        },
        ttl_seconds=ttl,
    )
    html_link = f"{base_url}/api/v1/reports/delivery/download?token={html_token}"
    docx_link = f"{base_url}/api/v1/reports/delivery/download?token={docx_token}"

    output_language = doc.get("output_language") or "tr"
    subject, body_html, body_plain = build_report_ready_email(
        incident_id=incident_id,
        output_language=output_language,
        docx_link=docx_link,
    )

    html_bytes, attach_name = _load_report_html_bytes(doc)
    attachments = []
    if html_bytes:
        attachments.append((attach_name, html_bytes, "text/html"))
    else:
        # Fallback when attachment unavailable — include HTML download link in body
        fallback_note_tr = (
            f'<p><a href="{html_link}">HTML raporu indir</a> (24 saat geçerli)</p>'
        )
        fallback_note_en = (
            f'<p><a href="{html_link}">Download HTML report</a> (valid 24 hours)</p>'
        )
        note = fallback_note_en if normalize_delivery_lang(output_language) == "en" else fallback_note_tr
        body_html = body_html + note
        body_plain = body_plain + f"\nHTML: {html_link}\n"

    ok, msg_id, err = send_email(
        doc.get("recipient_email") or "",
        subject,
        body_html,
        text_body=body_plain,
        attachments=attachments or None,
    )
    if ok:
        doc["status"] = "sent"
        doc["sent_at"] = _utc_now_iso()
        doc["provider_message_id"] = msg_id
        doc["last_error"] = ""
    else:
        doc["last_error"] = err or "send_failed"
        doc["status"] = "failed_permanent" if attempt >= max_attempts else "failed"
    _save_doc(doc)
    return {"ok": ok, "status": doc.get("status"), "error": err}


def reset_memory_store() -> None:
    _mem_deliveries.clear()


def maybe_enqueue_report_email(
    *,
    tenant_id: str,
    owner_user_id: str,
    recipient_email: str,
    report_id: str,
    incident_id: str,
    artifact_version: str = "v1",
    user_prefs: Optional[dict] = None,
    output_language: str = "tr",
    html_path: str = "",
    docx_path: str = "",
    library_item_id: str = "",
) -> Optional[dict[str, Any]]:
    """Idempotent enqueue used by all report-ready API paths."""
    return enqueue_report_ready_email(
        tenant_id=tenant_id,
        owner_user_id=owner_user_id,
        recipient_email=recipient_email,
        report_id=report_id,
        incident_id=incident_id,
        artifact_version=artifact_version,
        user_prefs=user_prefs,
        output_language=output_language,
        html_path=html_path,
        docx_path=docx_path,
        library_item_id=library_item_id,
    )
