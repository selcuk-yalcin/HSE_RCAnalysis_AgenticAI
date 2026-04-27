"""
Smoke scenario for 3-5 parallel RCA runs.

Usage (manual):
  BASE_URL=http://localhost:8000 python tests/test_parallel_rca_load_scenario.py
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
import urllib.request


BASE_URL = (os.getenv("BASE_URL") or "http://localhost:8000").rstrip("/")
TENANT_ID = os.getenv("TENANT_ID", "default")
PARALLEL = int(os.getenv("PARALLEL_RUNS", "3"))


def _post(path: str, payload: dict):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Tenant-ID": TENANT_ID},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _run_single(i: int):
    created = _post(
        "/api/v1/incidents/create",
        {
            "reported_by": "load-test",
            "date_time": "2026-04-27 10:00",
            "event_category": "near miss",
            "description": f"parallel load scenario {i}",
            "injury_description": "",
            "forwarded_to": "HSE",
        },
    )
    incident_id = ((created.get("data") or {}).get("incident_id") or "").strip()
    if not incident_id:
        raise RuntimeError(f"incident_id missing in create response: {created}")
    _post(
        f"/api/v1/incidents/{incident_id}/assessment",
        {"incident_id": incident_id, "event_type": "Incident", "actual_harm": "Minor", "riddor_reportable": "No"},
    )
    start = _post(
        f"/api/v1/incidents/{incident_id}/pipeline/start",
        {
            "location": "Plant",
            "who_involved": "Operator",
            "how_happened": "Technician bypassed LOTO during energized panel work.",
            "activities": "Maintenance",
            "working_conditions": "Busy shift",
            "safety_procedures": "LOTO exists but skipped",
            "injuries": "none",
            "why_probe_answers": [],
        },
    )
    return {"incident_id": incident_id, "job_id": (start.get("data") or {}).get("job_id")}


if __name__ == "__main__":
    print(f"Running parallel load smoke: parallel={PARALLEL} base_url={BASE_URL}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL) as ex:
        results = list(ex.map(_run_single, range(PARALLEL)))
    print("Load scenario submitted:", results)

