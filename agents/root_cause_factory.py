"""
Root cause + rapor agent fabrikası — API ve Celery ortak giriş noktası.

Varsayılan: V3.2 (olay-zarar W1 + A/B → C/D).
Override: ROOTCAUSE_AGENT_VERSION=3.1|3.2|v2
"""

from __future__ import annotations

import os
import traceback
from typing import Any, Tuple

DEFAULT_ROOTCAUSE_AGENT_VERSION = "3.2"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def resolve_root_cause_agent_version() -> str:
    """3.2 varsayılan; ROOTCAUSE_AGENT_VERSION ile override."""
    raw = (os.getenv("ROOTCAUSE_AGENT_VERSION") or DEFAULT_ROOTCAUSE_AGENT_VERSION).strip().lower()
    if raw in ("3.2", "v3.2", "32", "v32"):
        return "3.2"
    if raw in ("3.1", "v3.1", "31", "v31"):
        return "3.1"
    if raw in ("v2", "2", "legacy"):
        return "v2"
    return DEFAULT_ROOTCAUSE_AGENT_VERSION


def use_v3_2_agent() -> bool:
    return resolve_root_cause_agent_version() == "3.2"


def init_root_cause_agent(use_rag: bool | None = None) -> Tuple[object, str]:
    """
    V3.2 (varsayılan) → V3.1 → V2 fallback.
    ROOTCAUSE_ENGINE=v2|legacy V2'yi zorlar.
    """
    if use_rag is None:
        use_rag = _env_bool("ROOTCAUSE_USE_RAG", True)

    force_v2 = os.getenv("ROOTCAUSE_ENGINE", "").strip().lower() in ("v2", "2", "legacy")
    if force_v2:
        from agents.rootcause_agent_v2 import RootCauseAgentV2

        return RootCauseAgentV2(use_rag=use_rag), "v2 (ROOTCAUSE_ENGINE forced)"

    version = resolve_root_cause_agent_version()

    if version == "3.2":
        try:
            from agents.v3_2.rootcause_agent_v3_2 import RootCauseAgentV3_2
            from agents.rca_cost_profile import get_rca_cost_profile, root_cause_agent_kwargs

            kwargs = root_cause_agent_kwargs(use_rag)
            agent = RootCauseAgentV3_2(**kwargs)
            prof = get_rca_cost_profile()
            return agent, f"v3.2 ({prof.name})"
        except Exception as e:
            print(f"⚠️  V3.2 başlatılamadı, V3.1 deneniyor: {e}")
            traceback.print_exc()

    try:
        from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
        from agents.rca_cost_profile import get_rca_cost_profile, root_cause_agent_kwargs

        kwargs = root_cause_agent_kwargs(use_rag)
        agent = RootCauseAgentV3_1(**kwargs)
        prof = get_rca_cost_profile()
        return agent, f"v3.1 ({prof.name})"
    except Exception as e:
        print(f"⚠️  V3.1 başlatılamadı, V2 kullanılıyor: {e}")
        traceback.print_exc()
        from agents.rootcause_agent_v2 import RootCauseAgentV2

        return RootCauseAgentV2(use_rag=use_rag), f"v2 (fallback after v3.1 error: {e})"


def init_report_agent() -> Tuple[object, str]:
    """V3.2 aktifken SkillBasedDocxAgentV32 (why_chain pin)."""
    if use_v3_2_agent():
        try:
            from agents.v3_2.skillbased_docx_agent_v3_2 import SkillBasedDocxAgentV32

            return SkillBasedDocxAgentV32(), "SkillBasedDocxAgentV32"
        except Exception as e:
            print(f"⚠️  SkillBasedDocxAgentV32 yüklenemedi, V3.1 rapor: {e}")
            traceback.print_exc()

    from agents.skillbased_docx_agent import SkillBasedDocxAgent

    return SkillBasedDocxAgent(), "SkillBasedDocxAgent"
