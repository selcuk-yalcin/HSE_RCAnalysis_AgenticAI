"""
MongoDB Atlas Vector Search Index Oluşturma
============================================

Kullanım:
    python rag_pipeline/retrieval/setup_vector_search_index.py
    python rag_pipeline/retrieval/setup_vector_search_index.py --collection taxonomy_barsel

Önkoşul: koleksiyonda `embedding` alanı dolu dokümanlar (build_mongodb_vector_store.py).
Not: Mevcut retriever client-side cosine kullanır; Atlas index opsiyonel hızlandırma.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.server_api import ServerApi

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

DEFAULT_COLLECTION = "taxonomy_barsel"
INDEX_NAME_SUFFIX = "_vector_search"
EMBEDDING_DIM = 384


def _index_definition() -> dict:
    return {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "cosine",
                "numDimensions": EMBEDDING_DIM,
            },
            {"type": "filter", "path": "code"},
            {"type": "filter", "path": "cause_type"},
            {"type": "filter", "path": "taxonomy_source"},
            {"type": "filter", "path": "section_ids"},
        ]
    }


def create_vector_search_index(collection_name: str = DEFAULT_COLLECTION) -> None:
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI ortam değişkeni bulunamadı.")

    print("=" * 70)
    print(f"🔍 Atlas Vector Search — rca.{collection_name}")
    print("=" * 70)

    client = MongoClient(mongo_uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    print("✓ MongoDB bağlantısı başarılı!")

    db = client.rca
    collection = db[collection_name]
    doc_count = collection.count_documents({})
    with_emb = collection.count_documents({"embedding": {"$exists": True, "$ne": []}})
    print(f"✓ Doküman: {doc_count} (embedding'li: {with_emb})")

    if with_emb == 0:
        print(
            "\n⚠️  Koleksiyonda embedding yok. Önce:\n"
            "   python rag_pipeline/indexing/build_mongodb_vector_store.py --backend hash"
        )
        client.close()
        return

    index_name = f"{collection_name}{INDEX_NAME_SUFFIX}"
    definition = _index_definition()

    existing = []
    try:
        existing = list(collection.list_search_indexes())
    except Exception as exc:
        print(f"\n⚠️  list_search_indexes desteklenmiyor: {exc}")
        _print_manual_atlas_ui(collection_name, index_name, definition)
        client.close()
        return

    if any(idx.get("name") == index_name for idx in existing):
        print(f"\n⚠️  Index '{index_name}' zaten mevcut.")
        for idx in existing:
            if idx.get("name") == index_name:
                print(f"   status={idx.get('status')} queryable={idx.get('queryable')}")
    else:
        print(f"\n➕ Index oluşturuluyor: {index_name}")
        model = SearchIndexModel(
            definition=definition,
            name=index_name,
            type="vectorSearch",
        )
        result = collection.create_search_index(model)
        print(f"✓ create_search_index → {result}")
        print("   Senkronizasyon birkaç dakika sürebilir (Atlas UI → Search Indexes).")

    print("\n" + "=" * 70)
    print("🎉 Vector Search index isteği tamamlandı")
    print("=" * 70)
    client.close()


def _print_manual_atlas_ui(collection_name: str, index_name: str, definition: dict) -> None:
    import json

    print("\n📋 Atlas UI ile manuel oluşturma:")
    print(f"   Database: rca | Collection: {collection_name} | Index name: {index_name}")
    print("   Atlas → Browse Collections → Search Indexes → Create Search Index → JSON Editor")
    print(json.dumps(definition, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--collection",
        default=os.getenv("TAXONOMY_COLLECTION", DEFAULT_COLLECTION),
    )
    args = p.parse_args()
    create_vector_search_index(args.collection)
