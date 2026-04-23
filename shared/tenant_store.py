"""
Multi-tenant in-memory stores (API process).
Each tenant has isolated incidents_db and jobs_db.
Celery workers sync incidents via tenant_id in pipeline results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

DEFAULT_TENANT_ID = "default"


@dataclass
class TenantStore:
    incidents_db: Dict[str, Any] = field(default_factory=dict)
    jobs_db: Dict[str, Any] = field(default_factory=dict)


_registry: Dict[str, TenantStore] = {}


def get_tenant_store(tenant_id: str | None) -> TenantStore:
    tid = (tenant_id or "").strip() or DEFAULT_TENANT_ID
    if len(tid) > 128:
        tid = tid[:128]
    if tid not in _registry:
        _registry[tid] = TenantStore()
    return _registry[tid]


def tenant_namespace_prefix(tenant_id: str | None) -> str:
    tid = (tenant_id or "").strip() or DEFAULT_TENANT_ID
    return f"tenant:{tid}"


def all_tenants_summary() -> Dict[str, Any]:
    return {
        tid: {"incidents": len(s.incidents_db), "jobs": len(s.jobs_db)}
        for tid, s in _registry.items()
    }


def total_incidents_across_tenants() -> int:
    return sum(len(s.incidents_db) for s in _registry.values())
