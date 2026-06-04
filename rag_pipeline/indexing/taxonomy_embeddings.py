"""
Taxonomy embedding backends — torch opsiyonel.

Production (Railway worker): TAXONOMY_EMBEDDING_BACKEND=sentence_transformers
  → import ve query aynı backend; Mongo'daki `embedding` alanı kullanılır.

Yerel dev (bozuk torch): TAXONOMY_EMBEDDING_BACKEND=hash
  → import + query ikisi de hash; ST ile yüklenmiş Mongo ile uyumsuz olur.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Any, Dict, List, Literal, Optional, Tuple

Backend = Literal["auto", "sentence_transformers", "hash", "none"]
DEFAULT_DIM = 384
DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
ENV_BACKEND = "TAXONOMY_EMBEDDING_BACKEND"


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[\w\u00c0-\u024f]+", (text or "").lower(), flags=re.UNICODE)


def hash_embed_text(text: str, dim: int = DEFAULT_DIM) -> List[float]:
    """Deterministic bag-of-tokens hash embedding (L2-normalized). Torch gerektirmez."""
    vec = [0.0] * dim
    for tok in _tokenize(text):
        digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def resolve_embedding_backend(override: Optional[str] = None) -> Backend:
    """Ortam / argümandan backend seçimi (auto | sentence_transformers | hash | none)."""
    raw = (override or os.getenv(ENV_BACKEND) or "auto").strip().lower()
    if raw in ("auto", "sentence_transformers", "hash", "none"):
        return raw  # type: ignore[return-value]
    return "auto"


def build_embedding_meta(
    backend_used: str,
    *,
    model_name: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIM,
) -> Dict[str, Any]:
    return {
        "backend": backend_used,
        "model": model_name if backend_used == "sentence_transformers" else "",
        "dimensions": dimensions,
    }


def validate_embedding_alignment(
    stored_meta: Optional[Dict[str, Any]],
    query_backend: str,
    *,
    strict: bool = False,
) -> Tuple[bool, str]:
    """
    Mongo `embedding_meta.backend` ile query backend uyumu.
    strict=True → sentence_transformers zorunlu ama ST yoksa hata.
    """
    if not stored_meta:
        return True, ""

    stored = str(stored_meta.get("backend") or "").strip()
    if not stored or stored == query_backend:
        return True, ""

    msg = (
        f"Embedding backend uyumsuz: Mongo={stored!r}, query={query_backend!r}. "
        f"Retrieval kalitesi düşer. "
        f"Çözüm: aynı backend ile yeniden import "
        f"(build_mongodb_vector_store.py --backend {query_backend}) "
        f"veya TAXONOMY_EMBEDDING_BACKEND={stored!r} ayarlayın."
    )
    if strict and stored == "sentence_transformers" and query_backend == "hash":
        raise RuntimeError(msg)
    return False, msg


def probe_effective_backend(backend: Backend = "auto") -> Backend:
    """`auto` için embed_texts'in gerçekte kullanacağı backend'i döndür."""
    if backend in ("hash", "none", "sentence_transformers"):
        return backend
    _, used = embed_texts(["probe"], backend="auto")
    return used  # type: ignore[return-value]


def _sentence_transformer_embed(texts: List[str], model_name: str) -> List[List[float]]:
    from sentence_transformers import SentenceTransformer  # noqa: WPS433

    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, convert_to_tensor=False, show_progress_bar=len(texts) > 8)
    return [v.tolist() for v in vectors]


def embed_texts(
    texts: List[str],
    *,
    backend: Backend = "auto",
    model_name: str = DEFAULT_MODEL,
    dimensions: int = DEFAULT_DIM,
) -> Tuple[List[List[float]], str]:
    """
    Returns (embeddings, backend_used).
    backend=none → empty list (caller skips embedding field).
    """
    if backend == "none":
        return [], "none"

    if backend in ("auto", "sentence_transformers"):
        try:
            vectors = _sentence_transformer_embed(texts, model_name)
            return vectors, "sentence_transformers"
        except Exception as exc:
            if backend == "sentence_transformers":
                raise RuntimeError(
                    "sentence_transformers yüklenemedi. Torch kurulumunu düzeltin veya "
                    "TAXONOMY_EMBEDDING_BACKEND=hash kullanın."
                ) from exc
            print(
                f"⚠️  sentence_transformers kullanılamıyor ({exc}). "
                f"Hash embedding fallback ({dimensions}d) kullanılıyor."
            )

    vectors = [hash_embed_text(t, dim=dimensions) for t in texts]
    return vectors, "hash"
