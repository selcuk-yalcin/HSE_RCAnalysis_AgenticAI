"""Redis incident merge helper (pipeline part3 sync)."""

from unittest.mock import MagicMock, patch


def test_merge_incident_fields_merges_part3():
    from shared.incident_persistence import merge_incident_fields, incident_redis_key

    store = {}

    mock_client = MagicMock()

    def fake_setex(key, ttl, payload):
        store[key] = payload

    def fake_get(key):
        return store.get(key)

    mock_client.setex.side_effect = fake_setex
    mock_client.get.side_effect = fake_get

    with patch("shared.incident_persistence.get_redis_client", return_value=mock_client):
        ok = merge_incident_fields(
            "tenant-a",
            "INC-1",
            {"part3": {"root_causes": [{"code": "D4.9"}]}, "status": "completed"},
        )
        assert ok is True
        key = incident_redis_key("tenant-a", "INC-1")
        assert "part3" in store[key]
        assert "D4.9" in store[key]
