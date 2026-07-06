"""Root cause factory birim testleri."""

from agents.root_cause_factory import (
    DEFAULT_ROOTCAUSE_AGENT_VERSION,
    resolve_root_cause_agent_version,
    use_v3_2_agent,
)


def test_default_agent_version_is_3_2():
    assert DEFAULT_ROOTCAUSE_AGENT_VERSION == "3.2"


def test_resolve_version_defaults_to_3_2(monkeypatch):
    monkeypatch.delenv("ROOTCAUSE_AGENT_VERSION", raising=False)
    assert resolve_root_cause_agent_version() == "3.2"
    assert use_v3_2_agent() is True


def test_resolve_version_3_1_override(monkeypatch):
    monkeypatch.setenv("ROOTCAUSE_AGENT_VERSION", "3.1")
    assert resolve_root_cause_agent_version() == "3.1"
    assert use_v3_2_agent() is False
