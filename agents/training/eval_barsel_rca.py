"""
BARSEL RAG retrieval evaluation (R8).

Mongo: rca.taxonomy_barsel (MONGODB_URI)
JSON fallback: in-memory fixture when --offline

Kullanım:
  python agents/training/eval_barsel_rca.py
  python agents/training/eval_barsel_rca.py --compare-modes
  python agents/training/eval_barsel_rca.py --offline
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_GOLD = Path(__file__).parent / "data" / "barsel_rca_gold.jsonl"


def _load_gold(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _load_retriever(*, offline: bool):
    if offline:
        from tests.test_barsel_taxonomy_retrieval import FIXTURE_DOCS
        from rag_pipeline.retrieval.barsel_taxonomy_retriever import BarselTaxonomyRetriever

        return BarselTaxonomyRetriever(documents=FIXTURE_DOCS), "offline_fixture"

    uri = (os.getenv("MONGODB_URI") or "").strip()
    if not uri:
        return None, "no_mongodb_uri"

    from rag_pipeline.retrieval.barsel_taxonomy_retriever import BarselTaxonomyRetriever

    r = BarselTaxonomyRetriever()
    if not r.connected:
        return None, "mongo_unreachable"
    db = "rca"
    col = os.getenv("TAXONOMY_COLLECTION", "taxonomy_barsel")
    return r, f"mongodb://{db}.{col} ({len(r._docs)} docs)"


def _eval_scenario(
    row: Dict[str, Any],
    retriever: Any,
    *,
    k: int,
    mode_label: str,
) -> Dict[str, Any]:
    from agents.training.barsel_eval_metrics import (
        any_hit_at_k,
        band_purity,
        recall_at_k,
    )

    query = row.get("incident_summary") or ""
    gold_imm = row.get("gold_immediate_codes") or []
    gold_root = row.get("gold_root_codes") or []

    imm_hits_a = retriever.retrieve(query, k=k, band="A", min_score=0.01)
    imm_hits_b = retriever.retrieve(query, k=k, band="B", min_score=0.01)
    imm_codes = [h["code"] for h in imm_hits_a + imm_hits_b]

    root_hits_c = retriever.retrieve(
        query, k=max(3, k // 2), band="C", min_score=0.01
    )
    root_hits_d = retriever.retrieve(query, k=k, band="D", min_score=0.01)
    root_codes = [h["code"] for h in root_hits_c + root_hits_d]

    return {
        "id": row.get("id"),
        "mode": mode_label,
        "immediate_recall_at_k": recall_at_k(imm_codes, gold_imm, k * 2),
        "root_recall_at_k": recall_at_k(root_codes, gold_root, k + max(3, k // 2)),
        "immediate_any_hit": any_hit_at_k(imm_codes, gold_imm, k * 2),
        "root_any_hit": any_hit_at_k(root_codes, gold_root, k + max(3, k // 2)),
        "immediate_band_purity": (
            band_purity(imm_codes, "A", k) + band_purity(imm_codes, "B", k)
        )
        / 2.0,
        "root_band_purity": (
            band_purity(root_codes, "C", max(3, k // 2))
            + band_purity(root_codes, "D", k)
        )
        / 2.0,
        "retrieved_immediate": imm_codes[: k * 2],
        "retrieved_root": root_codes[: k + max(3, k // 2)],
        "gold_immediate": gold_imm,
        "gold_root": gold_root,
    }


def _run_eval(
    gold_rows: List[Dict[str, Any]],
    retriever: Any,
    *,
    k: int,
    mode_label: str,
) -> Dict[str, Any]:
    from agents.training.barsel_eval_metrics import aggregate_retrieval_report

    detail = [_eval_scenario(row, retriever, k=k, mode_label=mode_label) for row in gold_rows]
    return {
        "mode": mode_label,
        "k": k,
        "summary": aggregate_retrieval_report(detail),
        "scenarios": detail,
    }


def _static_prompt_retriever():
    """Statik mod simülasyonu: band içi ilk k kod (RAG öncesi davranış proxy)."""
    from agents.barsel_taxonomy import _ensure_index, _BAND

    _ensure_index()

    class _Static:
        connected = True

        def retrieve(self, query, k=5, band=None, min_score=0.05, **kwargs):  # noqa: ARG002
            b = (band or "A").upper()
            items = _BAND.get(b, [])[:k]
            out = []
            for item in items:
                out.append(
                    {
                        "code": item.code,
                        "content": {"tr": {"title": item.title, "definition": item.definition[:200]}},
                        "similarityScore": 0.5,
                    }
                )
            return out

    return _Static(), "static_json_first_k"


def main() -> None:
    parser = argparse.ArgumentParser(description="BARSEL RAG eval (R8)")
    parser.add_argument("--gold", default=str(DEFAULT_GOLD), help="Gold JSONL path")
    parser.add_argument("--k", type=int, default=int(os.getenv("ROOTCAUSE_TAXONOMY_RAG_K") or "8"))
    parser.add_argument("--offline", action="store_true", help="Mongo yok; fixture retriever")
    parser.add_argument(
        "--compare-modes",
        action="store_true",
        help="RAG (Mongo) vs statik ilk-k karşılaştırması",
    )
    parser.add_argument("--json-out", default="", help="Sonuçları JSON dosyaya yaz")
    args = parser.parse_args()

    gold_path = Path(args.gold)
    if not gold_path.is_file():
        raise SystemExit(f"Gold set bulunamadı: {gold_path}")

    gold_rows = _load_gold(gold_path)
    print(f"Gold senaryo: {len(gold_rows)} | k={args.k}")
    print(f"MONGODB_URI set: {bool((os.getenv('MONGODB_URI') or '').strip())}")
    print(f"TAXONOMY_COLLECTION: {os.getenv('TAXONOMY_COLLECTION', 'taxonomy_barsel')}")
    print(f"DB hedefi: rca.{os.getenv('TAXONOMY_COLLECTION', 'taxonomy_barsel')}")
    print()

    reports: List[Dict[str, Any]] = []

    retriever, source = _load_retriever(offline=args.offline)
    if retriever is None:
        print(f"⚠️  Retriever yok ({source}); --offline ile tekrar deneyin.")
        if not args.compare_modes:
            raise SystemExit(1)
    else:
        print(f"Retriever: {source}")
        reports.append(_run_eval(gold_rows, retriever, k=args.k, mode_label=f"rag_{source}"))

    if args.compare_modes:
        static_r, static_label = _static_prompt_retriever()
        reports.append(_run_eval(gold_rows, static_r, k=args.k, mode_label=static_label))

    for rep in reports:
        s = rep["summary"]
        print(f"=== {rep['mode']} ===")
        print(f"  immediate any-hit @k: {s.get('immediate_any_hit_rate', 0):.0%}")
        print(f"  immediate recall mean:  {s.get('immediate_recall_at_k_mean', 0):.0%}")
        print(f"  root any-hit @k:      {s.get('root_any_hit_rate', 0):.0%}")
        print(f"  root recall mean:     {s.get('root_recall_at_k_mean', 0):.0%}")
        print()

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Yazıldı: {out_path}")


if __name__ == "__main__":
    main()
