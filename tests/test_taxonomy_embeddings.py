"""taxonomy_embeddings + retriever alignment tests."""

import os

import pytest

from rag_pipeline.indexing.taxonomy_embeddings import (
    build_embedding_meta,
    hash_embed_text,
    resolve_embedding_backend,
    validate_embedding_alignment,
)
from rag_pipeline.retrieval.barsel_taxonomy_retriever import BarselTaxonomyRetriever


def test_resolve_embedding_backend_from_env(monkeypatch):
    monkeypatch.delenv("TAXONOMY_EMBEDDING_BACKEND", raising=False)
    assert resolve_embedding_backend() == "auto"
    monkeypatch.setenv("TAXONOMY_EMBEDDING_BACKEND", "hash")
    assert resolve_embedding_backend() == "hash"
    assert resolve_embedding_backend("sentence_transformers") == "sentence_transformers"


def test_validate_alignment_match():
    meta = build_embedding_meta("hash")
    ok, msg = validate_embedding_alignment(meta, "hash")
    assert ok and not msg


def test_validate_alignment_mismatch():
    meta = build_embedding_meta("sentence_transformers", model_name="paraphrase-multilingual-MiniLM-L12-v2")
    ok, msg = validate_embedding_alignment(meta, "hash")
    assert not ok
    assert "uyumsuz" in msg.lower() or "Mismatch" in msg or "Mongo" in msg


def test_validate_alignment_strict_raises():
    meta = build_embedding_meta("sentence_transformers")
    with pytest.raises(RuntimeError):
        validate_embedding_alignment(meta, "hash", strict=True)


def test_retriever_uses_stored_mongo_embeddings():
    text = "Tek çalışanın bilerek kural ihlali."
    emb = hash_embed_text(text)
    docs = [
        {
            "code": "A1.1",
            "cause_type": "immediate_cause",
            "section_ids": ["A"],
            "keywords": {"tr": ["bilerek ihlal"]},
            "content": {
                "tr": {
                    "title": "Bireysel Kural İhlali",
                    "definition": text,
                    "typical_problems": [],
                }
            },
            "embedding": emb,
            "embedding_meta": build_embedding_meta("hash"),
        }
    ]
    r = BarselTaxonomyRetriever(documents=docs, embedding_backend="hash")
    hits = r.retrieve_hits("bilerek kasıtlı kural ihlali", k=1)
    assert hits
    assert hits[0].code == "A1.1"


def test_retriever_warns_on_backend_mismatch(monkeypatch, caplog):
    import logging

    caplog.set_level(logging.WARNING)
    docs = [
        {
            "code": "A1.1",
            "cause_type": "immediate_cause",
            "section_ids": ["A"],
            "keywords": {"tr": ["test"]},
            "content": {"tr": {"title": "T", "definition": "d", "typical_problems": []}},
            "embedding": [0.1] * 384,
            "embedding_meta": build_embedding_meta("sentence_transformers"),
        }
    ]
    monkeypatch.setenv("TAXONOMY_EMBEDDING_BACKEND", "hash")
    r = BarselTaxonomyRetriever(documents=docs, embedding_backend="hash")
    assert r.connected
    assert any("uyumsuz" in rec.message.lower() or "Mongo" in rec.message for rec in caplog.records)
