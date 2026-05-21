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
) -> None:
    _ctx.set(
        {
            "tenant_id": (tenant_id or "default").strip()[:128],
            "owner_user_id": (owner_user_id or "anonymous").strip()[:256],
            "module": (module or "deepwhy").strip()[:64],
        }
    )


def clear_usage_context() -> None:
    _ctx.set(None)


def get_usage_context() -> Optional[dict[str, str]]:
    return _ctx.get()


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
    ctx = get_usage_context()
    if not ctx:
        return None
    usage = getattr(response, "usage", None)
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
    if not prompt_tokens and not completion_tokens:
        return None
    from shared import token_account

    return token_account.debit_tokens(
        ctx["tenant_id"],
        ctx["owner_user_id"],
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        reason=reason,
        module=ctx.get("module") or "deepwhy",
        incident_id=incident_id,
        job_id=job_id,
        operation_label=operation_label,
        idempotency_key=idempotency_key,
        model=model or getattr(response, "model", "") or "",
    )
