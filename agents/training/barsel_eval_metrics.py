"""
BARSEL RCA evaluation metrics (R8).

Retrieval: gold kod top-k içinde mi?
Band: dönen kodlar doğru A/B/C/D bandında mı?
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence, Set

_CODE_RE = re.compile(r"\b([ABCD]\d+\.\d+)\b", re.IGNORECASE)


def normalize_codes(codes: Iterable[str]) -> Set[str]:
    out: Set[str] = set()
    for raw in codes or []:
        c = (raw or "").strip().upper()
        if not c:
            continue
        m = _CODE_RE.search(c.replace(" ", ""))
        if m:
            out.add(m.group(1).upper())
        elif re.match(r"^[ABCD]\d+\.\d+$", c):
            out.add(c)
    return out


def band_of(code: str) -> str:
    return (code or "").strip().upper()[:1]


def recall_at_k(retrieved: Sequence[str], gold: Iterable[str], k: int) -> float:
    """Gold kodlardan en az biri top-k retrieved içinde mi? (0/1 per gold set, averaged)."""
    gold_set = normalize_codes(gold)
    if not gold_set:
        return 0.0
    top = normalize_codes(list(retrieved)[:k])
    if not top:
        return 0.0
    hits = len(gold_set.intersection(top))
    return hits / len(gold_set)


def any_hit_at_k(retrieved: Sequence[str], gold: Iterable[str], k: int) -> bool:
    gold_set = normalize_codes(gold)
    top = normalize_codes(list(retrieved)[:k])
    return bool(gold_set.intersection(top))


def band_purity(retrieved: Sequence[str], expected_band: str, k: int) -> float:
    """Top-k içindeki kodların beklenen band (A/B/C/D) oranı."""
    band = (expected_band or "").upper()[:1]
    if band not in "ABCD":
        return 0.0
    top = [c for c in normalize_codes(list(retrieved)[:k])]
    if not top:
        return 0.0
    ok = sum(1 for c in top if band_of(c) == band)
    return ok / len(top)


def aggregate_retrieval_report(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not rows:
        return {"n": 0}
    n = len(rows)
    return {
        "n": n,
        "immediate_recall_at_k_mean": round(
            sum(r.get("immediate_recall_at_k", 0.0) for r in rows) / n, 4
        ),
        "root_recall_at_k_mean": round(
            sum(r.get("root_recall_at_k", 0.0) for r in rows) / n, 4
        ),
        "immediate_any_hit_rate": round(
            sum(1 for r in rows if r.get("immediate_any_hit")) / n, 4
        ),
        "root_any_hit_rate": round(
            sum(1 for r in rows if r.get("root_any_hit")) / n, 4
        ),
        "immediate_band_purity_mean": round(
            sum(r.get("immediate_band_purity", 0.0) for r in rows) / n, 4
        ),
        "root_band_purity_mean": round(
            sum(r.get("root_band_purity", 0.0) for r in rows) / n, 4
        ),
    }
