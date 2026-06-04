"""
Build MongoDB Vector Store — BARSEL taksonomi (RAG)
===================================================

    python rag_pipeline/parsing/normalize_barsel_vectordb.py
    python rag_pipeline/indexing/build_mongodb_vector_store.py

Gerekli env: MONGODB_URI
Koleksiyon: rca.taxonomy_barsel (TAXONOMY_COLLECTION ile override)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient
from pymongo.server_api import ServerApi

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from rag_pipeline.indexing.barsel_rag_document import (  # noqa: E402
    BarselRagDocument,
    load_jsonl,
    normalize_vectordb_record,
)
from rag_pipeline.indexing.taxonomy_embeddings import (  # noqa: E402
    DEFAULT_DIM,
    DEFAULT_MODEL,
    build_embedding_meta,
    embed_texts,
    resolve_embedding_backend,
)

load_dotenv()

DEFAULT_COLLECTION = "taxonomy_barsel"
DEFAULT_JSONL = project_root / "rag_pipeline/data/processed/barsel_taxonomy_rag.jsonl"
FALLBACK_JSONL = project_root / "rag_pipeline/data/processed/barsel_taxonomy_vectordb.jsonl"


class MongoVectorStoreBuilder:
    """BARSEL RAG JSONL → MongoDB + embedding."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        embedding_backend: str = "auto",
    ):
        self.model_name = model_name
        self.embedding_backend = embedding_backend
        self.barsel_docs: List[BarselRagDocument] = []
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        self.collection_name = DEFAULT_COLLECTION
        self.last_backend_used = ""

    def connect_to_db(self, collection_name: str) -> None:
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI ortam değişkeni bulunamadı.")

        print("🗄️ MongoDB'ye bağlanılıyor...")
        self.client = MongoClient(mongo_uri, server_api=ServerApi("1"))
        self.client.admin.command("ping")
        print("✓ MongoDB bağlantısı başarılı!")

        self.db = self.client.rca
        self.collection_name = collection_name
        self.collection = self.db[collection_name]
        print(f"✓ Koleksiyon: rca.{collection_name}")

    def load_barsel_jsonl(self, jsonl_path: Path, *, normalize_raw: bool = False) -> None:
        if not jsonl_path.exists():
            raise FileNotFoundError(jsonl_path)
        print(f"📚 BARSEL JSONL: {jsonl_path.name}")
        rows = load_jsonl(jsonl_path)
        docs: List[BarselRagDocument] = []
        for row in rows:
            if normalize_raw or row.get("doc_type") == "taxonomy_item":
                docs.append(normalize_vectordb_record(row))
            else:
                docs.append(BarselRagDocument(**row))
        self.barsel_docs = docs
        print(f"✓ {len(self.barsel_docs)} BARSEL kod yüklendi.")

    def _ensure_indexes(self) -> None:
        assert self.collection is not None
        self.collection.create_index([("code", ASCENDING)], unique=True)
        self.collection.create_index([("taxonomy_source", ASCENDING)])
        self.collection.create_index([("cause_type", ASCENDING)])
        self.collection.create_index([("section_ids", ASCENDING)])
        print("✓ Indexler: code (unique), taxonomy_source, cause_type, section_ids")

    def build_and_upload(self, *, replace: bool = True) -> int:
        assert self.collection is not None

        if not self.barsel_docs:
            print("⚠️ Yüklenecek BARSEL kaydı yok.")
            return 0

        if replace:
            deleted = self.collection.delete_many({})
            print(f"🗑️ Koleksiyon temizlendi: {deleted.deleted_count} kayıt")

        texts_to_embed = [doc.embedding_text() for doc in self.barsel_docs]
        embeddings, backend_used = embed_texts(
            texts_to_embed,
            backend=self.embedding_backend,  # type: ignore[arg-type]
            model_name=self.model_name,
            dimensions=DEFAULT_DIM,
        )
        self.last_backend_used = backend_used
        emb_meta = build_embedding_meta(
            backend_used,
            model_name=self.model_name,
            dimensions=DEFAULT_DIM,
        )
        if backend_used == "sentence_transformers":
            print(f"🤖 Embedding: {self.model_name} (sentence_transformers)")
        elif backend_used == "hash":
            print(f"🤖 Embedding: hash fallback ({DEFAULT_DIM} boyut, torch gerekmez)")
        else:
            print("⚠️ Embedding atlanıyor (--backend none); vektör arama devre dışı.")

        documents_to_upload = []
        for i, rag_doc in enumerate(self.barsel_docs):
            emb = embeddings[i] if embeddings else None
            documents_to_upload.append(
                rag_doc.to_mongo_document(
                    embedding=emb,
                    embedding_meta=emb_meta if emb is not None else None,
                )
            )

        print(f"⬆️ {len(documents_to_upload)} belge yükleniyor...")
        self.collection.insert_many(documents_to_upload)
        self._ensure_indexes()
        print(f"✅ {len(documents_to_upload)} belge → rca.{self.collection_name}")
        return len(documents_to_upload)

    def close_connection(self) -> None:
        if self.client:
            self.client.close()
            print("🔌 MongoDB bağlantısı kapatıldı.")


def _resolve_input(input_path: Optional[str]) -> tuple[Path, bool]:
    if input_path:
        return Path(input_path), False
    if DEFAULT_JSONL.exists():
        return DEFAULT_JSONL, False
    if FALLBACK_JSONL.exists():
        return FALLBACK_JSONL, True
    raise FileNotFoundError(
        f"BARSEL JSONL bulunamadı. Önce: python rag_pipeline/parsing/normalize_barsel_vectordb.py"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="MongoDB BARSEL taxonomy vector store builder")
    parser.add_argument("--input", help="barsel_taxonomy_rag.jsonl yolu (opsiyonel)")
    parser.add_argument(
        "--collection",
        default=os.getenv("TAXONOMY_COLLECTION", DEFAULT_COLLECTION),
        help=f"Mongo koleksiyon adı (varsayılan: {DEFAULT_COLLECTION})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="SentenceTransformer model adı (--backend sentence_transformers|auto)",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "sentence_transformers", "hash", "none"),
        default=resolve_embedding_backend(),
        help="Production: sentence_transformers | Yerel dev: hash | auto: ST dene, olmazsa hash",
    )
    args = parser.parse_args()

    input_path, normalize_raw = _resolve_input(args.input)

    print("=" * 70)
    print(f"MongoDB Vector Store — BARSEL → rca.{args.collection}")
    print("=" * 70)

    builder = MongoVectorStoreBuilder(
        model_name=args.model,
        embedding_backend=args.backend,
    )
    try:
        builder.connect_to_db(args.collection)
        builder.load_barsel_jsonl(input_path, normalize_raw=normalize_raw)
        count = builder.build_and_upload()
        print("=" * 70)
        print(f"🎉 Tamamlandı — {count} doküman (embedding: {builder.last_backend_used or 'n/a'})")
        print("=" * 70)
        print(
            f"\nSonraki adım (Atlas): python rag_pipeline/retrieval/setup_vector_search_index.py "
            f"--collection {args.collection}"
        )
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        builder.close_connection()


if __name__ == "__main__":
    main()
