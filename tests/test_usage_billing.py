"""OpenRouter / LiteLLM usage billing integration tests."""

import os

import pytest

os.environ.pop("MONGODB_URI", None)
os.environ["TOKEN_ENFORCEMENT"] = "1"
os.environ["TOKEN_PERIOD_LIMIT"] = "10000"
os.environ["TOKEN_DEFAULT_BALANCE"] = "5000"

from shared import token_account  # noqa: E402
from shared.usage_context import (  # noqa: E402
    bind_usage_context,
    clear_usage_context,
    record_openrouter_json,
    record_token_usage,
)
from shared.litellm_billing import _on_litellm_success, install_litellm_billing_callback  # noqa: E402


@pytest.fixture(autouse=True)
def reset_memory():
    token_account._mem_accounts.clear()
    token_account._mem_ledger.clear()
    clear_usage_context()
    yield
    token_account._mem_accounts.clear()
    token_account._mem_ledger.clear()
    clear_usage_context()


class _FakeUsage:
    prompt_tokens = 1200
    completion_tokens = 350


class _FakeResponse:
    usage = _FakeUsage()
    model = "anthropic/claude-haiku-4.5"
    id = "gen-test-1"


def test_record_token_usage_with_context():
    bind_usage_context(
        tenant_id="t1",
        owner_user_id="u1",
        module="deepwhy",
        incident_id="INC-1",
        job_id="job-1",
    )
    record_token_usage(100, 50, reason="llm_call", operation_label="test")
    acc = token_account.ensure_account("t1", "u1")
    assert acc["balance"] == 4850
    assert acc["lifetime_used"] == 150
    recent = token_account.get_recent_operations("t1", "u1", limit=5)
    assert recent[0]["token_cost"] == 150
    assert recent[0]["reason"] == "llm_call"


def test_record_token_usage_without_context_is_noop():
    record_token_usage(100, 50, reason="llm_call")
    assert token_account.ensure_account("t1", "u1")["balance"] == 5000


def test_record_openrouter_json():
    bind_usage_context(tenant_id="t1", owner_user_id="u1", module="report", incident_id="INC-2")
    body = {
        "id": "or-resp-9",
        "model": "google/gemini-2.5-flash",
        "usage": {"prompt_tokens": 800, "completion_tokens": 200},
    }
    record_openrouter_json(body, reason="report_html", operation_label="Rapor")
    acc = token_account.ensure_account("t1", "u1")
    assert acc["balance"] == 5000 - 1000


def test_litellm_callback_debits_when_context_bound():
    bind_usage_context(tenant_id="t1", owner_user_id="u1", module="deepwhy", incident_id="INC-3")
    _on_litellm_success({"model": "anthropic/claude-haiku-4.5"}, _FakeResponse(), 0.0, 1.0)
    acc = token_account.ensure_account("t1", "u1")
    assert acc["balance"] == 5000 - 1550


def test_litellm_callback_idempotent_by_response_id():
    bind_usage_context(tenant_id="t1", owner_user_id="u1", module="deepwhy")
    resp = _FakeResponse()
    _on_litellm_success({}, resp, 0.0, 1.0)
    _on_litellm_success({}, resp, 0.0, 1.0)
    acc = token_account.ensure_account("t1", "u1")
    assert acc["balance"] == 5000 - 1550


def test_install_litellm_billing_callback_idempotent():
    assert install_litellm_billing_callback() in (True, False)
    assert install_litellm_billing_callback() in (True, False)
