from shared.signed_links import sign_payload, verify_token


def test_sign_and_verify_roundtrip():
    token = sign_payload(
        {"tenant_id": "t1", "owner_user_id": "u1", "incident_id": "inc-1", "artifact": "html"},
        ttl_seconds=120,
    )
    payload = verify_token(token)
    assert payload is not None
    assert payload["tenant_id"] == "t1"
    assert payload["incident_id"] == "inc-1"


def test_expired_token_rejected(monkeypatch):
    token = sign_payload({"tenant_id": "t1"}, ttl_seconds=3600)
    monkeypatch.setattr("shared.signed_links.time.time", lambda: 9_999_999_999)
    assert verify_token(token) is None
