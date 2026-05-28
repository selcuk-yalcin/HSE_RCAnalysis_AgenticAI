"""
HMAC-signed, time-limited download tokens (P0.10).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional


def _secret() -> bytes:
    raw = (os.getenv("REPORT_LINK_SIGNING_SECRET") or os.getenv("SECRET_KEY") or "dev-report-link-secret").encode()
    return raw


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def sign_payload(payload: Dict[str, Any], *, ttl_seconds: int = 86400) -> str:
    body = dict(payload)
    body["exp"] = int(time.time()) + max(60, int(ttl_seconds))
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(_secret(), raw, hashlib.sha256).digest()
    return f"{_b64url_encode(raw)}.{_b64url_encode(sig)}"


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    if not token or "." not in token:
        return None
    raw_b64, sig_b64 = token.split(".", 1)
    try:
        raw = _b64url_decode(raw_b64)
        sig = _b64url_decode(sig_b64)
        expected = hmac.new(_secret(), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(raw.decode("utf-8"))
        if int(payload.get("exp") or 0) < int(time.time()):
            return None
        return payload
    except Exception:  # noqa: BLE001
        return None
