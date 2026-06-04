"""
Taxonomy embedding backends — torch opsiyonel.

Production: sentence_transformers (384-dim MiniLM).
Yerel fallback: hash embedding (torch/sklearn gerekmez) — import/dev için.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import List, Literal, Tuple

Backend = Literal["auto", "sentence_transformers", "hash", "none"]
DEFAULT_DIM = 384
DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


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


def _sentence_transformer_embed(texts: List[str], model_name: str) -> List[List[float]]:
    from sentence_transformers import SentenceTransformer  # noqa: WPS433

    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, convert_to_tensor=False, show_progress_bar=True)
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
                    "--backend hash kullanın."
                ) from exc
            print(
                f"⚠️  sentence_transformers kullanılamıyor ({exc}). "
                f"Hash embedding fallback ({dimensions}d) kullanılıyor."
            )

    vectors = [hash_embed_text(t, dim=dimensions) for t in texts]
    return vectors, "hash"
