import os

import pytest

os.environ.pop("MONGODB_URI", None)

from shared import report_deliveries  # noqa: E402


@pytest.fixture(autouse=True)
def reset_deliveries():
    report_deliveries.reset_memory_store()
    yield
    report_deliveries.reset_memory_store()


def test_delivery_idempotency_in_memory():
    doc1 = report_deliveries.enqueue_report_ready_email(
        tenant_id="t1",
        owner_user_id="user_a",
        recipient_email="user@example.com",
        report_id="rep-1",
        incident_id="inc-1",
        artifact_version="v1",
    )
    assert doc1 is not None
    doc2 = report_deliveries.enqueue_report_ready_email(
        tenant_id="t1",
        owner_user_id="user_a",
        recipient_email="user@example.com",
        report_id="rep-1",
        incident_id="inc-1",
        artifact_version="v1",
    )
    assert doc2["delivery_key"] == doc1["delivery_key"]
