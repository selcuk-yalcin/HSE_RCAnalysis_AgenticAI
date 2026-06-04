"""
RAG Pipeline Retrieval Module
============================

query_mongodb_vector_store (SentenceTransformers) ağır bir import'tur; bu pakette
sadece RAGAnalyzer hemen yüklenir. MongoVectorRetriever `__getattr__` ile ertelenir.
"""

from .rag_agent_integration import RAGAnalyzer

__all__ = [
    "MongoVectorRetriever",
    "BarselTaxonomyRetriever",
    "RAGAnalyzer",
]


def __getattr__(name: str):
    if name == "MongoVectorRetriever":
        from .query_mongodb_vector_store import MongoVectorRetriever
        return MongoVectorRetriever
    if name == "BarselTaxonomyRetriever":
        from .barsel_taxonomy_retriever import BarselTaxonomyRetriever
        return BarselTaxonomyRetriever
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
