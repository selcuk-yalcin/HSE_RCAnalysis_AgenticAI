"""
BARSEL iki aşamalı taksonomi retriever (R5).

1. eleme: keywords.tr overlap → aday daraltma (~156 → top_k_keyword)
2. eleme: definition + typical_problems embedding benzerliği → final_k

Torch gerekmez (hash embedding fallback). Mongo: rca.taxonomy_barsel
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from rag_pipeline.indexing.barsel_rag_document import parse_keywords
from rag_pipeline.indexing.taxonomy_embeddings import embed_texts

load_dotenv()

DEFAULT_COLLECTION = "taxonomy_barsel"
_TOKEN_RE = re.compile(r"[\w\u00c0-\u024f]+", re.UNICODE)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _tokens(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(_normalize(text)) if len(t) >= 2]


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


@dataclass
class BarselHit:
    code: str
    cause_type: str
    content: Dict[str, Any]
    keywords: List[str]
    keyword_score: float
    semantic_score: float
    combined_score: float
    exclusion_conditions: List[Any] = field(default_factory=list)
    section_ids: List[str] = field(default_factory=list)

    def to_result_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "cause_type": self.cause_type,
            "content": self.content,
            "exclusion_conditions": self.exclusion_conditions,
            "keywords": self.keywords,
            "section_ids": self.section_ids,
            "similarityScore": self.combined_score,
            "keywordScore": self.keyword_score,
            "semanticScore": self.semantic_score,
        }


class BarselTaxonomyRetriever:
    """
    MongoDB taxonomy_barsel + iki aşamalı skor.
    MongoVectorRetriever ile uyumlu `retrieve()` arayüzü.
    """

    def __init__(
        self,
        *,
        collection_name: Optional[str] = None,
        mongo_uri: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        embedding_backend: str = "auto",
        keyword_weight: float = 0.35,
        semantic_weight: float = 0.65,
    ):
        self.collection_name = collection_name or os.getenv(
            "TAXONOMY_COLLECTION", DEFAULT_COLLECTION
        )
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        self.embedding_backend = embedding_backend
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
        self.client: Optional[MongoClient] = None
        self.collection = None
        self._docs: List[Dict[str, Any]] = list(documents or [])
        self.connected = False

        if documents is not None:
            self.connected = bool(self._docs)
        elif self.mongo_uri:
            self._connect_and_load()

    def _connect_and_load(self) -> None:
        self.client = MongoClient(self.mongo_uri, server_api=ServerApi("1"))
        self.client.admin.command("ping")
        self.collection = self.client.rca[self.collection_name]
        self._docs = list(
            self.collection.find(
                {},
                {
                    "_id": 0,
                    "code": 1,
                    "cause_type": 1,
                    "content": 1,
                    "keywords": 1,
                    "retrieval": 1,
                    "exclusion_conditions": 1,
                    "section_ids": 1,
                },
            )
        )
        self.connected = bool(self._docs)

    def close(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
        self.connected = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _doc_keywords(doc: Dict[str, Any]) -> List[str]:
        raw = (doc.get("keywords") or {}).get("tr") or []
        if isinstance(raw, list) and raw:
            out: List[str] = []
            for item in raw:
                out.extend(parse_keywords(item))
            return list(dict.fromkeys(out))
        kw_text = (doc.get("retrieval") or {}).get("keyword_text") or ""
        return parse_keywords(kw_text)

    @staticmethod
    def _semantic_source(doc: Dict[str, Any]) -> str:
        tr = (doc.get("content") or {}).get("tr") or {}
        parts = [str(tr.get("definition") or "")]
        probs = tr.get("typical_problems") or []
        if isinstance(probs, list):
            parts.extend(str(p) for p in probs if p)
        sel = tr.get("selection_criteria")
        if sel:
            parts.append(str(sel))
        return " ".join(p for p in parts if p.strip())

    def keyword_score(self, query: str, doc: Dict[str, Any]) -> float:
        q_norm = _normalize(query)
        q_tokens = set(_tokens(query))
        keywords = self._doc_keywords(doc)
        if not keywords:
            return 0.0

        hits = 0.0
        for kw in keywords:
            kn = _normalize(kw)
            if len(kn) >= 3 and kn in q_norm:
                hits += 2.0
                continue
            kw_tokens = _tokens(kw)
            overlap = sum(1 for t in kw_tokens if t in q_tokens)
            if overlap:
                hits += overlap / max(len(kw_tokens), 1)

        return min(hits / max(len(keywords), 1), 1.0)

    def keyword_filter(
        self,
        query: str,
        *,
        top_k: int = 20,
        cause_type_filter: Optional[str] = None,
        band: Optional[str] = None,
    ) -> List[Tuple[Dict[str, Any], float]]:
        scored: List[Tuple[Dict[str, Any], float]] = []
        for doc in self._docs:
            if cause_type_filter and doc.get("cause_type") != cause_type_filter:
                continue
            if band:
                code = str(doc.get("code") or "")
                sections = doc.get("section_ids") or []
                if not (code.startswith(band) or band in sections):
                    continue
            s = self.keyword_score(query, doc)
            if s > 0:
                scored.append((doc, s))

        scored.sort(key=lambda x: x[1], reverse=True)
        if not scored:
            # fallback: tüm dokümanlara düşük skor ver (semantic aşaması kurtarır)
            pool = self._docs
            if cause_type_filter:
                pool = [d for d in pool if d.get("cause_type") == cause_type_filter]
            if band:
                pool = [
                    d
                    for d in pool
                    if str(d.get("code", "")).startswith(band) or band in (d.get("section_ids") or [])
                ]
            scored = [(d, 0.01) for d in pool[:top_k]]
        return scored[:top_k]

    def semantic_rerank(
        self,
        query: str,
        candidates: List[tuple[Dict[str, Any], float]],
        *,
        top_k: int = 5,
    ) -> List[BarselHit]:
        if not candidates:
            return []

        texts = [self._semantic_source(doc) for doc, _ in candidates]
        q_vecs, _ = embed_texts([query], backend=self.embedding_backend)  # type: ignore[arg-type]
        d_vecs, _ = embed_texts(texts, backend=self.embedding_backend)  # type: ignore[arg-type]
        q_vec = q_vecs[0] if q_vecs else []

        hits: List[BarselHit] = []
        for i, (doc, kw_score) in enumerate(candidates):
            sem = _cosine(q_vec, d_vecs[i]) if q_vec and d_vecs else 0.0
            combined = self.keyword_weight * kw_score + self.semantic_weight * sem
            tr = (doc.get("content") or {}).get("tr") or {}
            hits.append(
                BarselHit(
                    code=str(doc.get("code") or ""),
                    cause_type=str(doc.get("cause_type") or ""),
                    content=doc.get("content") or {"tr": tr},
                    keywords=self._doc_keywords(doc),
                    keyword_score=kw_score,
                    semantic_score=sem,
                    combined_score=combined,
                    exclusion_conditions=doc.get("exclusion_conditions") or [],
                    section_ids=doc.get("section_ids") or [],
                )
            )

        hits.sort(key=lambda h: h.combined_score, reverse=True)
        return hits[:top_k]

    def retrieve(
        self,
        query: str,
        k: int = 5,
        language: Optional[str] = None,  # noqa: ARG002 — BARSEL tr-only today
        cause_type_filter: Optional[str] = None,
        min_score: float = 0.05,
        keyword_pool: int = 20,
        band: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self.connected or not query.strip():
            return []

        candidates = self.keyword_filter(
            query,
            top_k=keyword_pool,
            cause_type_filter=cause_type_filter,
            band=band,
        )
        hits = self.semantic_rerank(query, candidates, top_k=k)
        return [h.to_result_dict() for h in hits if h.combined_score >= min_score]

    def retrieve_hits(self, query: str, **kwargs) -> List[BarselHit]:
        k = kwargs.pop("k", 5)
        keyword_pool = kwargs.pop("keyword_pool", 20)
        cause_type_filter = kwargs.get("cause_type_filter")
        band = kwargs.get("band")
        min_score = kwargs.get("min_score", 0.05)
        candidates = self.keyword_filter(
            query,
            top_k=keyword_pool,
            cause_type_filter=cause_type_filter,
            band=band,
        )
        return self.semantic_rerank(query, candidates, top_k=k)


def format_barsel_hits_for_prompt(hits: List[BarselHit], language: str = "tr") -> str:
    if not hits:
        return "Uygun BARSEL kodu bulunamadı."

    lines = ["=== BARSEL TAKSONOMİ (2-aşamalı retrieval) ===\n"]
    for i, hit in enumerate(hits, 1):
        tr = (hit.content.get(language) or hit.content.get("tr") or {})
        title = tr.get("title") or hit.code
        lines.append(
            f"\n{i}. [{hit.code}] {title} "
            f"(skor: {hit.combined_score:.2f} | kw: {hit.keyword_score:.2f} | sem: {hit.semantic_score:.2f})"
        )
        definition = tr.get("definition") or ""
        if definition:
            lines.append(f"   Tanım: {definition[:600]}")
        probs = tr.get("typical_problems") or []
        if probs:
            lines.append("   Tipik problemler:")
            for p in probs[:3]:
                lines.append(f"     • {p[:200]}")
        if hit.keywords:
            lines.append(f"   Anahtar kelimeler: {', '.join(hit.keywords[:8])}")
    return "\n".join(lines)
