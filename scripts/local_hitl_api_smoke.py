#!/usr/bin/env python3
"""Lokal HITL API smoke test (TestClient + isteğe bağlı canlı HTTP)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

HOW = """
Vardiya sonunda iki operatör forklift yakınında şaka yaparak birbirini korkuttu.
Biri bilerek güvenlik bariyerinin dışına çıktı; eğitimli personel olmasına rağmen
kasıtlı sapma olarak değerlendirilen davranış nedeniyle düşme riski oluştu.
""".strip()

ROOT_CAUSE = "İlk değerlendirme: A1.1, A4.3 adayları."

INCIDENT_ID = "INC-LOCAL-HITL-SMOKE"


def seed_incident(tenant_id: str = "default") -> None:
    from api.main import _save_incident_record

    _save_incident_record(
        tenant_id,
        INCIDENT_ID,
        {
            "id": INCIDENT_ID,
            "tenant_id": tenant_id,
            "status": "created",
            "created_at": datetime.now().isoformat(),
        },
    )


def run_testclient() -> dict:
    from fastapi.testclient import TestClient

    from api.main import app

    seed_incident()
    client = TestClient(app)
    headers = {"X-Tenant-ID": "default", "X-User-ID": "local-smoke-test"}
    body = {
        "how_happened": HOW,
        "root_cause_initial": ROOT_CAUSE,
        "answered_ids": [],
        "batch_size": 3,
        "output_language": "tr",
        "immediate_causes": [{"code": "A1.1", "cause_tr": "Bireysel kural ihlali"}],
    }
    r = client.post(
        f"/api/v1/incidents/{INCIDENT_ID}/hitl/questions",
        json=body,
        headers=headers,
    )
    print(f"TestClient status: {r.status_code}")
    if r.status_code != 200:
        print(r.text[:800])
        r.raise_for_status()
    return r.json()


def run_http(base: str = "http://127.0.0.1:8000") -> dict | None:
    try:
        import urllib.error
        import urllib.request
    except ImportError:
        return None

    body = json.dumps(
        {
            "how_happened": HOW,
            "root_cause_initial": ROOT_CAUSE,
            "answered_ids": [],
            "batch_size": 3,
            "output_language": "tr",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/v1/incidents/{INCIDENT_ID}/hitl/questions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": "default",
            "X-User-ID": "local-smoke-test",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:500]}")
        return None
    except Exception as e:
        print(f"Canlı HTTP atlandı ({e})")
        return None


def main() -> None:
    print("=== HITL API smoke (Mongo RAG) ===\n")
    os.environ.setdefault("HITL_USE_MONGO_RAG", "1")
    data = run_testclient()
    payload = data.get("data") or {}
    questions = payload.get("questions") or []
    print(f"cached={data.get('cached')} pool={payload.get('total_pool')} remaining={payload.get('remaining_after_batch')}\n")
    for i, q in enumerate(questions, 1):
        tr = q.get("question_tr") or q.get("soru") or ""
        src = q.get("source") or "?"
        print(f"{i}. [{src}] {tr[:140]}")

    eng = [q for q in questions if "Deliberate" in (q.get("question_tr") or "")]
    print(f"\nİngilizce HSG: {len(eng)} soru")
    kw = sum(1 for q in questions if "şaka" in (q.get("question_tr") or "").lower() or "bilerek" in (q.get("question_tr") or "").lower())
    print(f"Türkçe keyword çerçevesi (örnek): {kw} soru")

    live = run_http()
    if live:
        print("\n--- Canlı uvicorn yanıtı (ilk soru) ---")
        q0 = (live.get("data") or {}).get("questions") or []
        if q0:
            print((q0[0].get("question_tr") or "")[:160])


if __name__ == "__main__":
    main()
