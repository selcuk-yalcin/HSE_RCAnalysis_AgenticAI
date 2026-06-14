"""
Request-scoped billing context for LLM usage recording (API + worker).
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Optional

_ctx: ContextVar[Optional[dict[str, str]]] = ContextVar("usage_ctx", default=None)


def bind_usage_context(
    *,
    tenant_id: str,
    owner_user_id: str,
    module: str = "deepwhy",
    incident_id: str = "",
    job_id: str = "",
) -> None:
    _ctx.set(
        {
            "tenant_id": (tenant_id or "default").strip()[:128],
            "owner_user_id": (owner_user_id or "anonymous").strip()[:256],
            "module": (module or "deepwhy").strip()[:64],
            "incident_id": (incident_id or "").strip()[:128],
            "job_id": (job_id or "").strip()[:128],
        }
    )


def clear_usage_context() -> None:
    _ctx.set(None)


def get_usage_context() -> Optional[dict[str, str]]:
    return _ctx.get()


def record_token_usage(
    prompt_tokens: int,
    completion_tokens: int,
    *,
    reason: str,
    module: str = "",
    incident_id: str = "",
    job_id: str = "",
    operation_label: str = "",
    idempotency_key: str = "",
    model: str = "",
) -> Optional[dict[str, Any]]:
    """Debit balance from explicit token counts when usage context is bound."""
    ctx = get_usage_context()
    if not ctx:
        return None
    pt = int(prompt_tokens or 0)
    ct = int(completion_tokens or 0)
    if not pt and not ct:
        return None
    from shared import token_account

    return token_account.debit_tokens(
        ctx["tenant_id"],
        ctx["owner_user_id"],
        prompt_tokens=pt,
        completion_tokens=ct,
        reason=reason,
        module=module or ctx.get("module") or "deepwhy",
        incident_id=incident_id or ctx.get("incident_id") or "",
        job_id=job_id or ctx.get("job_id") or "",
        operation_label=operation_label or reason,
        idempotency_key=idempotency_key,
        model=model,
    )


def record_openai_completion(
    response: Any,
    *,
    reason: str,
    incident_id: str = "",
    job_id: str = "",
    operation_label: str = "",
    idempotency_key: str = "",
    model: str = "",
) -> Optional[dict[str, Any]]:
    """Record token usage from an OpenAI-compatible completion response."""
    usage = getattr(response, "usage", None)
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
    if not prompt_tokens and not completion_tokens:
        return None
    return record_token_usage(
        prompt_tokens,
        completion_tokens,
        reason=reason,
        incident_id=incident_id,
        job_id=job_id,
        operation_label=operation_label,
        idempotency_key=idempotency_key,
        model=model or getattr(response, "model", "") or "",
    )


def record_openrouter_json(
    body: dict,
    *,
    reason: str,
    incident_id: str = "",
    job_id: str = "",
    operation_label: str = "",
    idempotency_key: str = "",
    model: str = "",
) -> Optional[dict[str, Any]]:
    """Record usage from OpenRouter HTTP JSON (`usage` object on response body)."""
    usage = (body or {}).get("usage") or {}
    if not isinstance(usage, dict):
        usage = {}
    pt = int(usage.get("prompt_tokens") or 0)
    ct = int(usage.get("completion_tokens") or 0)
    if not pt and not ct:
        return None
    resp_model = str((body or {}).get("model") or model or "")
    resp_id = str((body or {}).get("id") or "")
    idem = idempotency_key or (f"openrouter:{resp_id}" if resp_id else "")
    return record_token_usage(
        pt,
        ct,
        reason=reason,
        incident_id=incident_id,
        job_id=job_id,
        operation_label=operation_label or reason,
        idempotency_key=idem,
        model=resp_model,
    )


def try_record_openai_completion(
    response: Any,
    *,
    reason: str,
    operation_label: str = "",
    model: str = "",
) -> None:
    """Best-effort wrapper for agent call sites."""
    try:
        record_openai_completion(
            response,
            reason=reason,
            operation_label=operation_label or reason,
            model=model,
        )
    except Exception:  # noqa: BLE001
        pass
