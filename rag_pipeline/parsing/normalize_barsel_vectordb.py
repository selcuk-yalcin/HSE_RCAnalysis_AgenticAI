"""
BARSEL vectordb JSONL → temiz RAG JSONL
=======================================

Ham:  rag_pipeline/data/processed/barsel_taxonomy_vectordb.jsonl
Çıktı: rag_pipeline/data/processed/barsel_taxonomy_rag.jsonl

Kullanım:
    python rag_pipeline/parsing/normalize_barsel_vectordb.py
    python rag_pipeline/parsing/normalize_barsel_vectordb.py --input ... --output ...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from rag_pipeline.indexing.barsel_rag_document import (  # noqa: E402
    load_jsonl,
    normalize_vectordb_record,
    write_jsonl,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize BARSEL vectordb JSONL for RAG/Mongo")
    parser.add_argument(
        "--input",
        default=str(project_root / "rag_pipeline/data/processed/barsel_taxonomy_vectordb.jsonl"),
    )
    parser.add_argument(
        "--output",
        default=str(project_root / "rag_pipeline/data/processed/barsel_taxonomy_rag.jsonl"),
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    raw_rows = load_jsonl(input_path)
    docs = [normalize_vectordb_record(row) for row in raw_rows]
    write_jsonl(docs, output_path)

    with_kw = sum(1 for d in docs if d.content["tr"].keywords)
    with_prob = sum(1 for d in docs if d.content["tr"].typical_problems)
    with_sel = sum(1 for d in docs if d.content["tr"].selection_criteria)

    print("=" * 60)
    print("BARSEL RAG normalize")
    print(f"  Input:  {input_path.name} ({len(raw_rows)} rows)")
    print(f"  Output: {output_path}")
    print(f"  Keywords:           {with_kw}/{len(docs)}")
    print(f"  typical_problems:   {with_prob}/{len(docs)}")
    print(f"  selection_criteria: {with_sel}/{len(docs)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
