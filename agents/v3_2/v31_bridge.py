"""
V3.1 paylaşılan bileşenler — V3.2 bunları yeniden kullanır (2329 satır kopyalanmaz).

rootcause_agent_v3_1.py tek dosyada şunları içerir; V3.2 yalnızca WhyChain + rapor
katmanını değiştirir:

| Bileşen | V3.1 sınıf/fonksiyon | V3.2 kullanımı |
|---------|----------------------|----------------|
| Doğrudan neden | ImmediateCauseFinder | RootCauseAgentV3_2 (miras) |
| 5-Why zinciri | WhyChain | **WhyChainV32** (override) |
| Dal eleştirisi | BranchCriticAgent | miras |
| Meta kök | MetaRootCauseSynthesizer | miras |
| BARSEL snap | barsel_taxonomy.* | miras + report pin |
| RAG / Mongo | _barsel_retriever, _incident_taxonomy_prompt | miras |
| Analiz gövdesi | _analyze_root_causes_impl | miras (+ W1 cache reset) |
| Rapor LLM | skillbased_docx_agent | **SkillBasedDocxAgentV32** |
| Rapor pin | — | **report_why_chain_v3_2** |
| Decision tree | decision_tree_mermaid | **DecisionTreeGeneratorV32** |
"""

from __future__ import annotations

# Re-export — V3.2 modülleri doğrudan v3_1'e import edebilir
try:
    from agents.rootcause_agent_v3_1 import (
        ImmediateCauseFinder,
        MetaRootCauseSynthesizer,
        RootCauseAgentV3_1,
        RootCauseModel,
        SemanticAnswerVerifier,
        WhyAnswer,
        WhyChain,
        WhyQuestion,
        WhyStepModel,
        check_v3_1_status,
    )
except ImportError:
    from ..rootcause_agent_v3_1 import (
        ImmediateCauseFinder,
        MetaRootCauseSynthesizer,
        RootCauseAgentV3_1,
        RootCauseModel,
        SemanticAnswerVerifier,
        WhyAnswer,
        WhyChain,
        WhyQuestion,
        WhyStepModel,
        check_v3_1_status,
    )

__all__ = [
    "ImmediateCauseFinder",
    "MetaRootCauseSynthesizer",
    "RootCauseAgentV3_1",
    "RootCauseModel",
    "SemanticAnswerVerifier",
    "WhyAnswer",
    "WhyChain",
    "WhyQuestion",
    "WhyStepModel",
    "check_v3_1_status",
]
