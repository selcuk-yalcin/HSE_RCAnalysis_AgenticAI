"""
Import `agents/knowledge.json` taxonomy into MongoDB (hgs_taxonomy database).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.hgs_taxonomy import parse_hsg_taxonomy_items


load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import HGS taxonomy into MongoDB")
    parser.add_argument("--source", default="agents/knowledge.json", help="Knowledge source file path")
    parser.add_argument("--mongo-db", default="hgs_taxonomy", help="Mongo database name")
    parser.add_argument("--mongo-collection", default="taxonomy_items", help="Mongo collection name")
    args = parser.parse_args()

    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI not configured.")

    items = parse_hsg_taxonomy_items(args.source)
    docs = []
    imported_at = datetime.utcnow().isoformat() + "Z"
    for item in items:
        doc = item.model_dump()
        doc["source"] = os.path.basename(args.source)
        doc["imported_at"] = imported_at
        docs.append(doc)

    client = MongoClient(uri, server_api=ServerApi("1"))
    col = client[args.mongo_db][args.mongo_collection]
    col.delete_many({"source": os.path.basename(args.source)})
    if docs:
        col.insert_many(docs)
    col.create_index("code")
    col.create_index([("category", 1), ("code", 1)])
    print(f"Imported {len(docs)} taxonomy docs to {args.mongo_db}.{args.mongo_collection}")
    client.close()


if __name__ == "__main__":
    main()

