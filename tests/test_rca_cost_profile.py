"""RCA cost profile defaults."""

from agents.rca_cost_profile import get_rca_cost_profile, root_cause_agent_kwargs


def test_balanced_default():
    p = get_rca_cost_profile()
    assert p.name == "balanced"
    assert p.use_chain_of_thought is False
    assert p.critic_max_regenerations == 1
    assert p.hitl_use_llm is False


def test_root_cause_kwargs():
    kw = root_cause_agent_kwargs(use_rag=True)
    assert kw["use_rag"] is True
    assert kw["max_branch_cap"] == 3
    assert kw["use_chain_of_thought"] is False
