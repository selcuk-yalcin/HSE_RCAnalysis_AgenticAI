"""
LiteLLM success callback — records OpenRouter token usage for DSPy / LiteLLM calls.
"""

from __future__ import annotations

from typing import Any, Optional

_installed = False


def _on_litellm_success(kwargs: dict, completion_response: Any, start_time: float, end_time: float) -> None:
    del start_time, end_time
    try:
        from shared.usage_context import get_usage_context, record_token_usage

        ctx = get_usage_context()
        if not ctx:
            return

        usage = getattr(completion_response, "usage", None)
        if usage is None and isinstance(completion_response, dict):
            usage = completion_response.get("usage")

        prompt_tokens = 0
        completion_tokens = 0
        if usage is not None:
            if isinstance(usage, dict):
                prompt_tokens = int(usage.get("prompt_tokens") or 0)
                completion_tokens = int(usage.get("completion_tokens") or 0)
            else:
                prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

        if not prompt_tokens and not completion_tokens:
            return

        model = str(
            getattr(completion_response, "model", "")
            or (kwargs or {}).get("model")
            or ""
        )
        response_id = str(getattr(completion_response, "id", "") or "")
        idem = f"litellm:{response_id}" if response_id else ""

        record_token_usage(
            prompt_tokens,
            completion_tokens,
            reason="llm_call",
            module=ctx.get("module") or "deepwhy",
            incident_id=ctx.get("incident_id") or "",
            job_id=ctx.get("job_id") or "",
            operation_label=f"LLM ({model})" if model else "LLM call",
            idempotency_key=idem,
            model=model,
        )
    except Exception:  # noqa: BLE001
        pass


def install_litellm_billing_callback() -> bool:
    """Register global LiteLLM callback once (API + Celery worker)."""
    global _installed
    if _installed:
        return True
    try:
        import litellm
    except ImportError:
        return False

    callbacks = getattr(litellm, "success_callback", None)
    if callbacks is None:
        litellm.success_callback = [_on_litellm_success]
    elif isinstance(callbacks, list):
        if _on_litellm_success not in callbacks:
            callbacks.append(_on_litellm_success)
    else:
        litellm.success_callback = [callbacks, _on_litellm_success]

    _installed = True
    return True
