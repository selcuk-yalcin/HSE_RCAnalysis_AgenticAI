"""
RCA OpenRouter maliyet profilleri — istek sayısı / rapor.

quality  ~50+ LLM calls (ChainOfThought + BranchCritic×3 + HITL LLM)
balanced ~25–35 calls (Predict 5-Why + critic×1, HITL rule-based) — varsayılan SaaS
economy  ~15–20 calls (Predict, critic kapalı, max 2 dal)
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RcaCostProfile:
    name: str
    use_chain_of_thought: bool
    enable_diversity_check: bool
    enable_branch_critic: bool
    critic_max_regenerations: int
    max_branch_cap: int  # 0 = yalnızca ciddiyet/benzerlik kuralı
    hitl_use_llm: bool


_PROFILES: dict[str, RcaCostProfile] = {
    "quality": RcaCostProfile(
        name="quality",
        use_chain_of_thought=True,
        enable_diversity_check=True,
        enable_branch_critic=True,
        critic_max_regenerations=3,
        max_branch_cap=0,
        hitl_use_llm=True,
    ),
    "balanced": RcaCostProfile(
        name="balanced",
        use_chain_of_thought=False,
        enable_diversity_check=True,
        enable_branch_critic=True,
        critic_max_regenerations=1,
        max_branch_cap=3,
        hitl_use_llm=False,
    ),
    "economy": RcaCostProfile(
        name="economy",
        use_chain_of_thought=False,
        enable_diversity_check=False,
        enable_branch_critic=False,
        critic_max_regenerations=0,
        max_branch_cap=2,
        hitl_use_llm=False,
    ),
}


def get_rca_cost_profile() -> RcaCostProfile:
    raw = (os.getenv("ROOTCAUSE_COST_PROFILE") or "balanced").strip().lower()
    return _PROFILES.get(raw, _PROFILES["balanced"])


def root_cause_agent_kwargs(use_rag: bool) -> dict:
    """RootCauseAgentV3_1 constructor kwargs."""
    p = get_rca_cost_profile()
    return {
        "use_rag": use_rag,
        "enable_diversity_check": p.enable_diversity_check,
        "enable_branch_critic": p.enable_branch_critic,
        "critic_max_regenerations": p.critic_max_regenerations,
        "use_chain_of_thought": p.use_chain_of_thought,
        "max_branch_cap": p.max_branch_cap,
    }


def hitl_llm_enabled_override() -> bool | None:
    """None → profil varsayılanı; açık HITL_USE_LLM env profili ezer."""
    explicit = (os.getenv("HITL_USE_LLM") or "").strip().lower()
    if explicit in ("0", "false", "no", "off"):
        return False
    if explicit in ("1", "true", "yes", "on"):
        return True
    return None
