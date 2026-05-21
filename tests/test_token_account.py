"""Token account service (in-memory backend)."""

import os

import pytest

# Force in-memory path
os.environ.pop("MONGODB_URI", None)
os.environ["TOKEN_ENFORCEMENT"] = "1"
os.environ["TOKEN_PERIOD_LIMIT"] = "10000"
os.environ["TOKEN_DEFAULT_BALANCE"] = "5000"

from shared import token_account  # noqa: E402


@pytest.fixture(autouse=True)
def reset_memory():
    token_account._mem_accounts.clear()
    token_account._mem_ledger.clear()
    yield
    token_account._mem_accounts.clear()
    token_account._mem_ledger.clear()


def test_ensure_account_defaults():
    acc = token_account.ensure_account("t1", "user_a")
    assert acc["balance"] == 5000
    assert acc["period_limit"] == 10000


def test_debit_and_idempotency():
    token_account.debit_tokens(
        "t1",
        "user_a",
        amount=100,
        reason="hitl_question",
        module="hitl",
        idempotency_key="idem-1",
    )
    acc = token_account.ensure_account("t1", "user_a")
    assert acc["balance"] == 4900
    token_account.debit_tokens(
        "t1",
        "user_a",
        amount=100,
        reason="hitl_question",
        module="hitl",
        idempotency_key="idem-1",
    )
    acc2 = token_account.ensure_account("t1", "user_a")
    assert acc2["balance"] == 4900


def test_insufficient_balance():
    token_account.debit_tokens("t1", "user_a", amount=4990, reason="pipeline", module="deepwhy")
    ok, msg = token_account.check_sufficient("t1", "user_a", 500)
    assert not ok
    assert "Yetersiz" in msg


def test_users_isolated():
    token_account.debit_tokens("t1", "user_a", amount=1000, reason="pipeline", module="deepwhy")
    acc_b = token_account.ensure_account("t1", "user_b")
    assert acc_b["balance"] == 5000


def test_usage_summary_and_recent():
    token_account.debit_tokens(
        "t1",
        "u1",
        amount=200,
        reason="hitl_question",
        module="hitl",
        operation_label="Test soru",
    )
    summary = token_account.get_usage_summary("t1", "u1")
    assert summary["ai_question_count"] >= 1
    recent = token_account.get_recent_operations("t1", "u1", limit=5)
    assert len(recent) >= 1
    assert recent[0]["token_cost"] == 200
