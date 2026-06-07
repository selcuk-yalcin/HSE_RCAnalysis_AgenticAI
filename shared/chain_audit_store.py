"""
P1.23-G5: 5-Why zinciri snap audit + chain quality kayıtları (MongoDB).

Her analiz sonrası dal başına snap override / düşük kalite vakaları yazılır.
İleride MIPROv2 eğitiminde "kötü örnek" havuzu olarak kullanılabilir.
Best-effort: MONGODB_URI yoksa veya yazım başarısızsa sessizce atlar (pipeline'ı bozmaz).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection

COLLECTION_NAME = "chain_audit"
_indexes_ensured = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_collection() -> Optional[Collection]:
    global _indexes_ensured
    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        return None
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
            [("tenant_id", ASCENDING), ("incident_id", ASCENDING), ("created_at", ASCENDING)],
            name="tenant_incident_created",
        )
        _indexes_ensured = True
    return col


def build_chain_audit_records(
    *,
    tenant_id: str,
    incident_id: str,
    part3: dict[str, Any],
    analysis_model_preset: str = "",
) -> list[dict[str, Any]]:
    """part3 (frontend dönüştürülmüş veya _v2_raw) içinden dal başına audit satırı üret."""
    raw = part3.get("_v2_raw") if isinstance(part3, dict) else None
    source = raw if isinstance(raw, dict) else part3
    branches = (source or {}).get("analysis_branches") or []
    now = _utc_now_iso()
    records: list[dict[str, Any]] = []
    for branch in branches:
        root = branch.get("root_cause") or {}
        why_chain = branch.get("why_chain") or []
        w5 = ""
        for w in why_chain:
            try:
                lvl = int(w.get("level") or w.get("number") or 0)
            except (TypeError, ValueError):
                lvl = 0
            if lvl >= 5:
                w5 = str(w.get("answer_tr") or w.get("answer") or "")
        records.append(
            {
                "tenant_id": tenant_id,
                "incident_id": incident_id,
                "branch_number": branch.get("branch_number"),
                "root_code": str(root.get("code") or ""),
                "root_cause_tr": str(root.get("cause_tr") or ""),
                "root_standard_title_tr": str(root.get("standard_title_tr") or ""),
                "why5_answer": w5,
                "snap_audit_jaccard": root.get("snap_audit_jaccard"),
                "snap_overridden": bool(root.get("snap_overridden")),
                "snap_rejected": bool(root.get("snap_rejected")),
                "chain_quality": branch.get("chain_quality"),
                "analysis_model_preset": analysis_model_preset or "",
                "created_at": now,
            }
        )
    return records


def record_chain_audit(
    *,
    tenant_id: str,
    incident_id: str,
    part3: dict[str, Any],
    analysis_model_preset: str = "",
) -> int:
    """Audit satırlarını Mongo'ya yaz. Yazılan satır sayısını döndürür (hata → 0)."""
    if (os.getenv("CHAIN_AUDIT_ENABLED") or "1").strip().lower() in ("0", "false", "no", "off"):
        return 0
    try:
        records = build_chain_audit_records(
            tenant_id=tenant_id,
            incident_id=incident_id,
            part3=part3,
            analysis_model_preset=analysis_model_preset,
        )
        if not records:
            return 0
        col = _get_collection()
        if col is None:
            return 0
        col.insert_many(records, ordered=False)
        return len(records)
    except Exception:  # noqa: BLE001
        return 0
