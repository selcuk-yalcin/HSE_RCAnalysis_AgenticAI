"""
Root Cause Agent V3.2 — trainset tarzı 5-Why (olay W1 + A/B cevap).

STATUS: INACTIVE — production hâlâ V3.1 kullanır.
Aktivasyon: orchestrator / api/main değişikliği gerekir (bilinçli opt-in).

V3.1'e sadık kalır; yalnızca WhyChain ve W1 semantiği değişir.
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
    V3.2: hse_dspy_trainset.json akışı.

    - W1 soru: olaydan trainset tarzı (tüm dallarda ortak)
    - W1 cevap: A/B immediate_cause + BARSEL Mongo
    - W2–W5: bir önceki cevaba LLM → C/D kök neden
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
            "✅ Root Cause Agent V3.2 hazır (INACTIVE — trainset W1 akışı, "
            "orchestrator bağlı değil)"
        )

    def _analyze_root_causes_impl(
        self,
        part1_data: Dict,
        part2_data: Dict,
        investigation_data: Dict = None,
        synthesize_meta_root: bool = True,
    ) -> Dict:
        self._progress(
            "BÖLÜM 3: Hiyerarşik kök neden analizi (V3.2 — trainset W1)",
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
            result["analysis_method"] = (
                "BARSEL Hierarchical 5-Why (DSPy V3.2 — trainset olay W1 + A/B cevap)"
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
    return {
        **base,
        "version": "3.2",
        "status": "INACTIVE (parallel implementation — opt-in only)",
        "active_in_production": False,
        "parent_agent": "RootCauseAgentV3_1",
        "why_chain_class": "WhyChainV32",
        "w1_question_style": "trainset — olaydan maruziyet/sonuç sorusu (ortak tüm dallarda)",
        "w1_answer_source": "A/B immediate_cause + BARSEL Mongo (evidence_tr öncelikli)",
        "w2_w5_style": "LLM zincir → C/D kök neden",
        "report_agent": "SkillBasedDocxAgentV32",
        "report_pin": "report_why_chain_v3_2.pin_agent_why_chains_to_report_v32",
        "decision_tree": "DecisionTreeGeneratorV32",
        "pipeline_entry": "pipeline_v3_2.run_v3_2_analysis_and_report",
        "rag_available": RAG_AVAILABLE,
        "reference_trainset": "good_tr_kimya_sizinti",
    }
