"""
Project-level Celery application.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from celery import Celery

# Worker startup fingerprint — bump on each deploy verification cycle so logs
# clearly show whether the running container has the latest code.
WORKER_BUILD_TAG = "rca-worker@2026-04-25T15:30Z openrouter-headers-v3"
print(f"🛠️  Celery worker module loaded — build={WORKER_BUILD_TAG}")


REDIS_URL = (os.getenv("REDIS_URL") or "redis://localhost:6379/0").strip()
BROKER_HEARTBEAT = int((os.getenv("CELERY_BROKER_HEARTBEAT") or "30").strip() or "30")
BROKER_POOL_LIMIT = int((os.getenv("CELERY_BROKER_POOL_LIMIT") or "10").strip() or "10")
VISIBILITY_TIMEOUT = int((os.getenv("CELERY_VISIBILITY_TIMEOUT") or "7200").strip() or "7200")
HEALTH_CHECK_INTERVAL = int((os.getenv("CELERY_HEALTH_CHECK_INTERVAL") or "20").strip() or "20")
WORKER_MAX_TASKS_PER_CHILD = int((os.getenv("CELERY_MAX_TASKS_PER_CHILD") or "25").strip() or "25")
WORKER_MAX_MEMORY_PER_CHILD = int((os.getenv("CELERY_MAX_MEMORY_PER_CHILD_KB") or "0").strip() or "0")

print(
    "🕒 Celery runtime clock check: "
    f"utc_now={datetime.now(timezone.utc).isoformat()}, "
    f"TZ={os.getenv('TZ', 'unset')}, "
    f"broker_heartbeat={BROKER_HEARTBEAT}s"
)

celery_app = Celery(
    "hse_rca_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.pipeline_tasks", "tasks.report_delivery_tasks"],
)

try:
    from shared.litellm_billing import install_litellm_billing_callback

    if install_litellm_billing_callback():
        print("✅ LiteLLM billing callback registered (worker)")
except Exception as _billing_exc:  # noqa: BLE001
    print(f"⚠️  LiteLLM billing callback skipped: {_billing_exc}")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    task_soft_time_limit=1500,
    result_expires=3600,
    broker_heartbeat=BROKER_HEARTBEAT,
    broker_heartbeat_checkrate=2,
    broker_pool_limit=BROKER_POOL_LIMIT,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,  # keep retrying on transient Railway/Redis blips
    broker_transport_options={
        "socket_connect_timeout": 30,
        "socket_timeout": 30,
        "socket_keepalive": True,
        "retry_on_timeout": True,
        "health_check_interval": HEALTH_CHECK_INTERVAL,
        "visibility_timeout": VISIBILITY_TIMEOUT,
    },
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=WORKER_MAX_TASKS_PER_CHILD,
    worker_max_memory_per_child=WORKER_MAX_MEMORY_PER_CHILD if WORKER_MAX_MEMORY_PER_CHILD > 0 else None,
)

