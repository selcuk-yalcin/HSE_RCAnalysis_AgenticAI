"""
Per-tenant, per-user token accounts and immutable usage ledger (P1.15).
Mongo when MONGODB_URI is set; in-process fallback for local dev.
"""

from __future__ import annotations

import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

ACCOUNTS_COLLECTION = "user_token_accounts"
LEDGER_COLLECTION = "token_ledger"
_indexes_ensured = False

# In-memory fallback
_mem_accounts: dict[str, dict[str, Any]] = {}
_mem_ledger: list[dict[str, Any]] = []


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _account_key(tenant_id: str, owner_user_id: str) -> str:
    return f"{tenant_id}|{owner_user_id}"


def enforcement_enabled() -> bool:
    raw = (os.getenv("TOKEN_ENFORCEMENT") or "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def period_limit() -> int:
    for name in ("TOKEN_PERIOD_LIMIT", "TOKEN_DEFAULT_LIMIT"):
        raw = (os.getenv(name) or "").strip()
        if raw:
            try:
                return max(1000, int(raw))
            except ValueError:
                pass
    return 220_000


def default_signup_balance() -> int:
    raw = (os.getenv("TOKEN_DEFAULT_BALANCE") or "").strip()
    if raw:
        try:
            return max(0, int(raw))
        except ValueError:
            pass
    return period_limit()


def estimate_cost(reason: str) -> int:
    """Fixed debit estimates when usage metadata is unavailable."""
    table = {
        "pipeline": int(os.getenv("TOKEN_PIPELINE_ESTIMATE") or "25000"),
        "investigate": int(os.getenv("TOKEN_INVESTIGATE_ESTIMATE") or "80000"),
        "assessment": int(os.getenv("TOKEN_ASSESSMENT_ESTIMATE") or "8000"),
        "actionplan": int(os.getenv("TOKEN_ACTIONPLAN_ESTIMATE") or "12000"),
        "report_html": int(os.getenv("TOKEN_REPORT_ESTIMATE") or "15000"),
        "report_docx": int(os.getenv("TOKEN_REPORT_ESTIMATE") or "15000"),
        "hitl_question": int(os.getenv("TOKEN_HITL_ESTIMATE") or "1500"),
    }
    return max(0, table.get(reason, 1000))


def _mongo_enabled() -> bool:
    return bool((os.getenv("MONGODB_URI") or "").strip())


def _db_name() -> str:
    return (
        os.getenv("MONGODB_REPORTS_DB")
        or os.getenv("MONGODB_DB")
        or os.getenv("MONGODB_DATABASE")
        or "rca"
    ).strip()


def _get_accounts_col() -> Collection:
    global _indexes_ensured
    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    col = client[_db_name()][ACCOUNTS_COLLECTION]
    if not _indexes_ensured:
        col.create_index(
            [("tenant_id", ASCENDING), ("owner_user_id", ASCENDING)],
            unique=True,
            name="tenant_owner_unique",
        )
        ledger = client[_db_name()][LEDGER_COLLECTION]
        ledger.create_index(
            [("tenant_id", ASCENDING), ("owner_user_id", ASCENDING), ("created_at", DESCENDING)],
            name="tenant_owner_created",
        )
        ledger.create_index(
            [("idempotency_key", ASCENDING)],
            unique=True,
            sparse=True,
            name="idempotency_unique",
        )
        _indexes_ensured = True
    return col


def _get_ledger_col() -> Collection:
    _get_accounts_col()
    uri = (os.getenv("MONGODB_URI") or "").strip()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return client[_db_name()][LEDGER_COLLECTION]


def store_location() -> dict[str, str]:
    return {
        "configured": _mongo_enabled(),
        "database": _db_name(),
        "accounts_collection": ACCOUNTS_COLLECTION,
        "ledger_collection": LEDGER_COLLECTION,
        "backend": "mongodb" if _mongo_enabled() else "memory",
    }


def ping_store() -> tuple[bool, str]:
    if not _mongo_enabled():
        return True, ""
    try:
        _get_accounts_col().database.client.admin.command("ping")
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def ensure_collections() -> dict[str, Any]:
    if _mongo_enabled():
        col = _get_accounts_col()
        n_acc = col.estimated_document_count()
        n_led = _get_ledger_col().estimated_document_count()
        return {**store_location(), "account_documents": n_acc, "ledger_documents": n_led}
    return {**store_location(), "account_documents": len(_mem_accounts), "ledger_documents": len(_mem_ledger)}


def _new_account_doc(tenant_id: str, owner_user_id: str) -> dict[str, Any]:
    limit = period_limit()
    balance = default_signup_balance()
    now = _utc_now_iso()
    return {
        "tenant_id": tenant_id,
        "owner_user_id": owner_user_id,
        "balance": balance,
        "reserved": 0,
        "period_limit": limit,
        "lifetime_used": 0,
        "plan_tier": (os.getenv("TOKEN_DEFAULT_PLAN_TIER") or "starter").strip(),
        "period_reset_at": now,
        "created_at": now,
        "updated_at": now,
    }


def ensure_account(tenant_id: str, owner_user_id: str) -> dict[str, Any]:
    tenant_id = (tenant_id or "default").strip()[:128]
    owner_user_id = (owner_user_id or "anonymous").strip()[:256]
    if _mongo_enabled():
        col = _get_accounts_col()
        doc = col.find_one({"tenant_id": tenant_id, "owner_user_id": owner_user_id})
        if doc:
            return _public_account(doc)
        fresh = _new_account_doc(tenant_id, owner_user_id)
        try:
            col.insert_one(fresh)
        except DuplicateKeyError:
            pass
        doc = col.find_one({"tenant_id": tenant_id, "owner_user_id": owner_user_id})
        return _public_account(doc or fresh)

    key = _account_key(tenant_id, owner_user_id)
    if key not in _mem_accounts:
        _mem_accounts[key] = _new_account_doc(tenant_id, owner_user_id)
    return _public_account(_mem_accounts[key])


def _public_account(doc: dict[str, Any]) -> dict[str, Any]:
    limit = int(doc.get("period_limit") or period_limit())
    balance = int(doc.get("balance") or 0)
    reserved = int(doc.get("reserved") or 0)
    used = max(0, limit - balance)
    pct = round((used / limit) * 100, 1) if limit > 0 else 0.0
    available = max(0, balance - reserved)
    return {
        "tenant_id": doc.get("tenant_id") or "",
        "owner_user_id": doc.get("owner_user_id") or "",
        "balance": balance,
        "reserved": reserved,
        "available": available,
        "period_limit": limit,
        "lifetime_used": int(doc.get("lifetime_used") or 0),
        "used": used,
        "used_percent": pct,
        "plan_tier": doc.get("plan_tier") or "starter",
        "period_reset_at": doc.get("period_reset_at") or "",
        "warn_level": _warn_level(pct),
    }


def _warn_level(used_percent: float) -> str:
    if used_percent >= 100:
        return "blocked"
    if used_percent >= 95:
        return "critical"
    if used_percent >= 80:
        return "warning"
    return "ok"


def check_sufficient(tenant_id: str, owner_user_id: str, amount: int) -> tuple[bool, str]:
    if not enforcement_enabled():
        return True, ""
    amount = max(0, int(amount))
    acc = ensure_account(tenant_id, owner_user_id)
    available = int(acc["available"])
    if available >= amount:
        return True, ""
    return (
        False,
        f"Yetersiz token bakiyesi (kalan: {available}, gereken: {amount}).",
    )


def reserve_tokens(
    tenant_id: str,
    owner_user_id: str,
    amount: int,
    *,
    idempotency_key: str = "",
) -> dict[str, Any]:
    amount = max(0, int(amount))
    ok, msg = check_sufficient(tenant_id, owner_user_id, amount)
    if not ok:
        raise InsufficientTokensError(msg)
    if _mongo_enabled():
        col = _get_accounts_col()
        res = col.find_one_and_update(
            {"tenant_id": tenant_id, "owner_user_id": owner_user_id},
            {"$inc": {"reserved": amount}, "$set": {"updated_at": _utc_now_iso()}},
            return_document=True,
        )
        return _public_account(res or ensure_account(tenant_id, owner_user_id))

    key = _account_key(tenant_id, owner_user_id)
    doc = _mem_accounts.setdefault(key, _new_account_doc(tenant_id, owner_user_id))
    doc["reserved"] = int(doc.get("reserved") or 0) + amount
    doc["updated_at"] = _utc_now_iso()
    return _public_account(doc)


def release_reserve(tenant_id: str, owner_user_id: str, amount: int) -> None:
    amount = max(0, int(amount))
    if _mongo_enabled():
        col = _get_accounts_col()
        col.update_one(
            {"tenant_id": tenant_id, "owner_user_id": owner_user_id},
            {
                "$inc": {"reserved": -amount},
                "$set": {"updated_at": _utc_now_iso()},
            },
        )
        return
    key = _account_key(tenant_id, owner_user_id)
    doc = _mem_accounts.get(key)
    if doc:
        doc["reserved"] = max(0, int(doc.get("reserved") or 0) - amount)


def _tokens_from_usage(
    prompt_tokens: int,
    completion_tokens: int,
    explicit_amount: int = 0,
) -> int:
    if explicit_amount > 0:
        return explicit_amount
    # Weight completion slightly higher (billing proxy)
    return max(1, int(prompt_tokens) + int(completion_tokens))


def debit_tokens(
    tenant_id: str,
    owner_user_id: str,
    *,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    amount: int = 0,
    reason: str,
    module: str = "deepwhy",
    incident_id: str = "",
    job_id: str = "",
    operation_label: str = "",
    idempotency_key: str = "",
    model: str = "",
    release_reserve_amount: int = 0,
) -> dict[str, Any]:
    """Debit balance; optional idempotency; optionally release reservation."""
    tenant_id = (tenant_id or "default").strip()[:128]
    owner_user_id = (owner_user_id or "anonymous").strip()[:256]
    cost = _tokens_from_usage(prompt_tokens, completion_tokens, amount)
    if cost <= 0:
        return ensure_account(tenant_id, owner_user_id)

    idem = (idempotency_key or "").strip()[:256]
    if idem:
        existing = _find_ledger_by_idempotency(idem)
        if existing:
            return ensure_account(tenant_id, owner_user_id)

    ensure_account(tenant_id, owner_user_id)
    entry = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "owner_user_id": owner_user_id,
        "delta": -cost,
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": cost,
        "reason": reason,
        "module": module,
        "incident_id": incident_id or "",
        "job_id": job_id or "",
        "operation_label": operation_label or reason,
        "model": model or "",
        "idempotency_key": idem or None,
        "created_at": _utc_now_iso(),
    }

    if _mongo_enabled():
        led = _get_ledger_col()
        try:
            led.insert_one(entry)
        except DuplicateKeyError:
            return ensure_account(tenant_id, owner_user_id)
        col = _get_accounts_col()
        inc: dict[str, Any] = {
            "balance": -cost,
            "lifetime_used": cost,
            "updated_at": _utc_now_iso(),
        }
        if release_reserve_amount > 0:
            inc["reserved"] = -int(release_reserve_amount)
        col.update_one(
            {"tenant_id": tenant_id, "owner_user_id": owner_user_id},
            {"$inc": inc},
        )
    else:
        _mem_ledger.append(entry)
        key = _account_key(tenant_id, owner_user_id)
        doc = _mem_accounts[key]
        doc["balance"] = max(0, int(doc.get("balance") or 0) - cost)
        doc["lifetime_used"] = int(doc.get("lifetime_used") or 0) + cost
        if release_reserve_amount > 0:
            doc["reserved"] = max(0, int(doc.get("reserved") or 0) - release_reserve_amount)
        doc["updated_at"] = _utc_now_iso()

    return ensure_account(tenant_id, owner_user_id)


def top_up(tenant_id: str, owner_user_id: str, amount: int, *, note: str = "manual_top_up") -> dict[str, Any]:
    amount = max(0, int(amount))
    ensure_account(tenant_id, owner_user_id)
    entry = {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "owner_user_id": owner_user_id,
        "delta": amount,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "reason": note,
        "module": "admin",
        "incident_id": "",
        "job_id": "",
        "operation_label": note,
        "model": "",
        "idempotency_key": None,
        "created_at": _utc_now_iso(),
    }
    if _mongo_enabled():
        _get_ledger_col().insert_one(entry)
        _get_accounts_col().update_one(
            {"tenant_id": tenant_id, "owner_user_id": owner_user_id},
            {"$inc": {"balance": amount}, "$set": {"updated_at": _utc_now_iso()}},
        )
    else:
        _mem_ledger.append(entry)
        key = _account_key(tenant_id, owner_user_id)
        _mem_accounts[key]["balance"] = int(_mem_accounts[key].get("balance") or 0) + amount
    return ensure_account(tenant_id, owner_user_id)


def _find_ledger_by_idempotency(key: str) -> Optional[dict]:
    if not key:
        return None
    if _mongo_enabled():
        return _get_ledger_col().find_one({"idempotency_key": key})
    for row in reversed(_mem_ledger):
        if row.get("idempotency_key") == key:
            return row
    return None


class InsufficientTokensError(Exception):
    """Raised when balance is too low for a billable operation."""


def get_usage_summary(tenant_id: str, owner_user_id: str) -> dict[str, Any]:
    acc = ensure_account(tenant_id, owner_user_id)
    since = _utc_now() - timedelta(days=30)
    hitl_count = _count_ledger(tenant_id, owner_user_id, reason_prefix="hitl", since=since)
    pipeline_count = _count_ledger(tenant_id, owner_user_id, reason="pipeline", since=since)
    return {
        **acc,
        "ai_question_count": hitl_count,
        "pipeline_runs_30d": pipeline_count,
        "enforcement_enabled": enforcement_enabled(),
    }


def get_timeseries(tenant_id: str, owner_user_id: str, days: int = 7) -> list[dict[str, Any]]:
    days = max(1, min(90, int(days)))
    start = _utc_now() - timedelta(days=days - 1)
    buckets: dict[str, int] = defaultdict(int)
    for i in range(days):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        buckets[d] = 0
    rows = _ledger_since(tenant_id, owner_user_id, start)
    for row in rows:
        if int(row.get("delta") or 0) >= 0:
            continue
        created = str(row.get("created_at") or "")[:10]
        if created in buckets:
            buckets[created] += abs(int(row.get("total_tokens") or 0))
    return [{"date": k, "tokens": buckets[k]} for k in sorted(buckets.keys())]


def get_module_breakdown(tenant_id: str, owner_user_id: str, days: int = 30) -> list[dict[str, Any]]:
    start = _utc_now() - timedelta(days=max(1, days))
    totals: dict[str, int] = defaultdict(int)
    for row in _ledger_since(tenant_id, owner_user_id, start):
        if int(row.get("delta") or 0) >= 0:
            continue
        mod = str(row.get("module") or "other")
        totals[mod] += abs(int(row.get("total_tokens") or 0))
    total = sum(totals.values()) or 1
    labels = {
        "deepwhy": "Kök Neden",
        "risk": "Risk Analizi",
        "bot": "Mevzuat Botu",
        "assessment": "Değerlendirme",
        "hitl": "HITL",
        "pipeline": "Pipeline",
        "report": "Rapor",
    }
    return [
        {
            "module": mod,
            "label": labels.get(mod, mod),
            "tokens": tok,
            "percent": round((tok / total) * 100, 1),
        }
        for mod, tok in sorted(totals.items(), key=lambda x: -x[1])
    ]


def get_recent_operations(
    tenant_id: str,
    owner_user_id: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    limit = max(1, min(100, int(limit)))
    rows = _ledger_list(tenant_id, owner_user_id, limit=limit)
    out = []
    for row in rows:
        if int(row.get("delta") or 0) >= 0:
            continue
        out.append(
            {
                "id": row.get("id") or "",
                "operation_label": row.get("operation_label") or row.get("reason") or "",
                "module": row.get("module") or "",
                "reason": row.get("reason") or "",
                "incident_id": row.get("incident_id") or "",
                "created_at": row.get("created_at") or "",
                "token_cost": abs(int(row.get("total_tokens") or 0)),
                "model": row.get("model") or "",
            }
        )
    return out


def _ledger_since(tenant_id: str, owner_user_id: str, since: datetime) -> list[dict]:
    if _mongo_enabled():
        cur = _get_ledger_col().find(
            {
                "tenant_id": tenant_id,
                "owner_user_id": owner_user_id,
                "created_at": {"$gte": since.isoformat()},
            }
        )
        return list(cur)
    iso = since.isoformat()
    return [
        r
        for r in _mem_ledger
        if r.get("tenant_id") == tenant_id
        and r.get("owner_user_id") == owner_user_id
        and str(r.get("created_at") or "") >= iso
    ]


def _ledger_list(tenant_id: str, owner_user_id: str, limit: int) -> list[dict]:
    if _mongo_enabled():
        cur = (
            _get_ledger_col()
            .find({"tenant_id": tenant_id, "owner_user_id": owner_user_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return list(cur)
    rows = [
        r
        for r in _mem_ledger
        if r.get("tenant_id") == tenant_id and r.get("owner_user_id") == owner_user_id
    ]
    rows.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return rows[:limit]


def _count_ledger(
    tenant_id: str,
    owner_user_id: str,
    *,
    reason: str = "",
    reason_prefix: str = "",
    since: Optional[datetime] = None,
) -> int:
    rows = _ledger_since(tenant_id, owner_user_id, since or (_utc_now() - timedelta(days=365)))
    n = 0
    for row in rows:
        if int(row.get("delta") or 0) >= 0:
            continue
        r = str(row.get("reason") or "")
        if reason and r != reason:
            continue
        if reason_prefix and not r.startswith(reason_prefix):
            continue
        n += 1
    return n
