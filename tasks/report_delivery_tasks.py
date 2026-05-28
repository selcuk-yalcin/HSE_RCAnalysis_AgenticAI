"""
Celery tasks for report completion email (P0.10).
"""

from __future__ import annotations

from celery_app import celery_app
from shared import report_deliveries


@celery_app.task(name="tasks.report_delivery_tasks.send_report_delivery_email", bind=True, max_retries=3)
def send_report_delivery_email(self, delivery_key: str) -> dict:
    result = report_deliveries.process_delivery(delivery_key)
    if result.get("ok"):
        return result
    if result.get("skipped"):
        return result
    # Exponential backoff: 60s, 300s, 1800s
    countdown = min(1800, 60 * (2 ** getattr(self.request, "retries", 0)))
    raise self.retry(countdown=countdown, exc=Exception(result.get("error") or "delivery_failed"))
