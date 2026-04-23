"""
Resolve tenant from headers / optional API key mapping.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from fastapi import Header

from shared.tenant_store import DEFAULT_TENANT_ID


def _load_api_key_map() -> dict:
    raw = (os.getenv("TENANT_API_KEYS_JSON") or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


async def resolve_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """
    Priority:
    1) X-API-Key matched in TENANT_API_KEYS_JSON {"sk-xxx": "tenant_slug"}
    2) X-Tenant-ID header
    3) default tenant
    """
    key_map = _load_api_key_map()
    if x_api_key and key_map:
        mapped = key_map.get(x_api_key.strip())
        if mapped:
            tid = str(mapped).strip()
            return tid[:128] if tid else DEFAULT_TENANT_ID
    if x_tenant_id:
        tid = x_tenant_id.strip()
        if tid:
            return tid[:128]
    return DEFAULT_TENANT_ID
