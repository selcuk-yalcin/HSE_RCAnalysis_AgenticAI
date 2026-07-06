"""
Root Cause Agent V3.2 — olay-zarar merkezli 5-Why (A/B → C/D).

STATUS: ACTIVE (varsayılan production — ROOTCAUSE_AGENT_VERSION=3.2)

V3.1 hatası:
  build_event_why1_question → "Neden … montaj meydana geldi?" (faaliyet cümlesi)

V3.2 akış (her kritik faktör):
  W1 — Ortak olay sorusu: "Neden Garcia … düşerek ağır yaralandı?"
  W1 cevap — Dal A/B mekanizması (BARSEL + evidence_tr)
  W2 — W1 cevabına neden
  W3–W5 — C/D kök neden
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
except ImportError:
    from ..rootcause_agent_v3_1 import RootCauseAgentV3_1

from .why_chain_v3_2 import WhyChainV32


class _WhyChainV32CallWrapper:
    """V3.1 analyze döngüsüne barsel_retriever enjekte eder."""

    def __init__(self, inner: WhyChainV32, agent: "RootCauseAgentV3_2") -> None:
        self._inner = inner
        self._agent = agent

    def __call__(self, **kwargs: Any) -> Dict:
        kwargs.setdefault("barsel_retriever", self._agent._barsel_retriever())
        return self._inner(**kwargs)

    def reset_shared_why1_cache(self) -> None:
        self._inner.reset_shared_why1_cache()

    @property
    def inner(self) -> WhyChainV32:
        return self._inner


class RootCauseAgentV3_2(RootCauseAgentV3_1):
    """
    V3.2: olay-zarar merkezli 5-Why.

    - W1 soru: tüm dallarda ortak (yaralanma/maruziyet merceği)
    - W1 cevap: dal başına A/B immediate_cause + BARSEL
    - W2: A/B cevabına neden
    - W3–W5: LLM → C/D kök neden
    """

    VERSION = "3.2"

    def __init__(
        self,
        use_rag: bool = False,
        enable_diversity_check: bool = True,
        enable_branch_critic: bool = True,
        critic_jaccard_threshold: float = 0.18,
        critic_max_regenerations: int = 3,
        *,
        use_chain_of_thought: bool = True,
        max_branch_cap: int = 0,
    ):
        self._v32_enable_diversity = enable_diversity_check
        self._v32_use_cot = use_chain_of_thought
        super().__init__(
            use_rag=use_rag,
            enable_diversity_check=enable_diversity_check,
            enable_branch_critic=enable_branch_critic,
            critic_jaccard_threshold=critic_jaccard_threshold,
            critic_max_regenerations=critic_max_regenerations,
            use_chain_of_thought=use_chain_of_thought,
            max_branch_cap=max_branch_cap,
        )
        inner = WhyChainV32(
            enable_diversity_check=enable_diversity_check,
            use_chain_of_thought=use_chain_of_thought,
        )
        self._why_chain_v32 = inner
        self.why_chain = _WhyChainV32CallWrapper(inner, self)
        print(
            "✅ Root Cause Agent V3.2 hazır (olay-zarar W1 + A/B→C/D)"
        )

    def _analyze_root_causes_impl(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None,
        synthesize_meta_root: bool = True,
    ) -> Dict:
        self._progress(
            "BÖLÜM 3: Hiyerarşik kök neden analizi (V3.2 — olay W1 + A/B→C/D)",
            stage="investigate",
            progress=12,
        )
        if hasattr(self.why_chain, "reset_shared_why1_cache"):
            self.why_chain.reset_shared_why1_cache()
        result = super()._analyze_root_causes_impl(
            part1_data,
            part2_data,
            investigation_data,
            synthesize_meta_root,
        )
        if isinstance(result, dict):
            shared_q = None
            inner = getattr(self.why_chain, "inner", None)
            if inner is not None:
                shared_q = getattr(inner, "shared_why1_question_cache", None)
            if shared_q:
                result["shared_why1_question"] = shared_q
            result["analysis_method"] = (
                "BARSEL Hierarchical 5-Why (DSPy V3.2 — olay W1 + A/B cevap → C/D kök)"
            )
            result["agent_version"] = self.VERSION
        return result


def create_v3_2_agent(
    use_rag: bool = False,
    enable_diversity: bool = True,
    **kwargs: Any,
) -> RootCauseAgentV3_2:
    """V3.2 agent fabrikası — production'da otomatik çağrılmaz."""
    return RootCauseAgentV3_2(
        use_rag=use_rag,
        enable_diversity_check=enable_diversity,
        **kwargs,
    )


def check_v3_2_status() -> Dict:
    try:
        from agents.rootcause_agent_v3_1 import RAG_AVAILABLE, check_v3_1_status
    except ImportError:
        from ..rootcause_agent_v3_1 import RAG_AVAILABLE, check_v3_1_status

    base = check_v3_1_status()
    from agents.root_cause_factory import resolve_root_cause_agent_version

    active = resolve_root_cause_agent_version() == "3.2"
    return {
        **base,
        "version": "3.2",
        "status": "ACTIVE (production default)" if active else "available (ROOTCAUSE_AGENT_VERSION≠3.2)",
        "active_in_production": active,
        "parent_agent": "RootCauseAgentV3_1",
        "why_chain_class": "WhyChainV32",
        "w1_question_style": "olay-zarar merceği — tüm dallarda ortak (ör. Garcia düşme yaralanması)",
        "w1_answer_source": "A/B immediate_cause + BARSEL Mongo (evidence_tr öncelikli)",
        "w2_style": "W1 A/B cevabına neden (build_direct_cause_why2_question)",
        "w3_w5_style": "LLM zincir → C/D kök neden",
        "v31_bug": "build_event_why1_question faaliyet cümlesi üretir (montaj/meydana geldi)",
        "report_agent": "SkillBasedDocxAgentV32",
        "report_pin": "report_why_chain_v3_2.pin_agent_why_chains_to_report_v32",
        "decision_tree": "DecisionTreeGeneratorV32",
        "pipeline_entry": "pipeline_v3_2.run_v3_2_analysis_and_report",
        "rag_available": RAG_AVAILABLE,
        "reference_trainset": "good_tr_kimya_sizinti",
    }
