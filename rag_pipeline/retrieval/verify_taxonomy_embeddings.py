"""
BARSEL Mongo embedding uyum kontrolü.

Kullanım:
    python rag_pipeline/retrieval/verify_taxonomy_embeddings.py
    TAXONOMY_EMBEDDING_BACKEND=sentence_transformers python rag_pipeline/retrieval/verify_taxonomy_embeddings.py

Çıkış kodu 0 = uyumlu veya meta yok (eski import); 1 = uyumsuz veya hata.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from rag_pipeline.indexing.taxonomy_embeddings import (  # noqa: E402
    ENV_BACKEND,
    probe_effective_backend,
    resolve_embedding_backend,
    validate_embedding_alignment,
)

load_dotenv(project_root / ".env")

DEFAULT_COLLECTION = "taxonomy_barsel"


def main() -> int:
    parser = argparse.ArgumentParser(description="BARSEL Mongo embedding backend doğrulama")
    parser.add_argument(
        "--collection",
        default=os.getenv("TAXONOMY_COLLECTION", DEFAULT_COLLECTION),
    )
    parser.add_argument(
        "--backend",
        default=None,
        help=f"Query backend (varsayılan: ${ENV_BACKEND} veya auto)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Uyumsuzlukta exit 1 + RuntimeError",
    )
    args = parser.parse_args()

    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI tanımlı değil.")
        return 1

    configured = resolve_embedding_backend(args.backend)
    effective = probe_effective_backend(configured)
    print(f"Query backend: configured={configured!r}, effective={effective!r}")

    client = MongoClient(mongo_uri, server_api=ServerApi("1"))
    try:
        client.admin.command("ping")
        coll = client.rca[args.collection]
        count = coll.count_documents({})
        sample = coll.find_one({"embedding_meta.backend": {"$exists": True}})
        meta = (sample or {}).get("embedding_meta") if sample else None
        with_emb = coll.count_documents({"embedding": {"$exists": True, "$ne": []}})

        print(f"Koleksiyon: rca.{args.collection} — {count} doküman, {with_emb} embedding'li")

        if not meta:
            print(
                "⚠️  embedding_meta yok (eski import). "
                "Yeniden import: python rag_pipeline/indexing/build_mongodb_vector_store.py "
                f"--backend {effective}"
            )
            return 0

        stored = meta.get("backend")
        print(f"Mongo embedding_meta: backend={stored!r}, model={meta.get('model')!r}, dim={meta.get('dimensions')}")

        ok, msg = validate_embedding_alignment(meta, effective, strict=args.strict)
        if ok:
            print("✅ Backend uyumlu.")
            return 0

        print(f"❌ {msg}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
