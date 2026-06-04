"""SentenceTransformer process cache."""

from unittest.mock import MagicMock, patch

from rag_pipeline.indexing import taxonomy_embeddings as te


def test_get_sentence_transformer_singleton():
    te.clear_sentence_transformer_cache()
    mock_cls = MagicMock()
    instance = MagicMock()
    mock_cls.return_value = instance

    fake_st = MagicMock(SentenceTransformer=mock_cls)
    with patch.dict("sys.modules", {"sentence_transformers": fake_st}):
        te.get_sentence_transformer("test-model-a")
        te.get_sentence_transformer("test-model-a")

    assert mock_cls.call_count == 1
    te.clear_sentence_transformer_cache()


def test_embed_texts_hash_no_st():
    te.clear_sentence_transformer_cache()
    vecs, backend = te.embed_texts(["hello world"], backend="hash")
    assert backend == "hash"
    assert len(vecs) == 1
    assert len(vecs[0]) == te.DEFAULT_DIM
