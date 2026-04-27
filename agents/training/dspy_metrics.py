"""
DSPy metrics for RCA WhyChain optimization.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


GENERIC_PATTERNS = {
    "insan hatası",
    "dikkatsizlik",
    "eğitim eksikliği",
    "ihmal",
    "human error",
    "lack of training",
    "carelessness",
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip().lower()


def chain_continuity_score(prediction: Dict[str, Any]) -> float:
    chain = prediction.get("why_chain") or []
    if not isinstance(chain, list) or len(chain) < 2:
        return 0.0
    hits = 0
    checks = 0
    for i in range(1, len(chain)):
        prev_answer = _safe_text((chain[i - 1] or {}).get("answer"))
        curr_question = _safe_text((chain[i] or {}).get("question"))
        if not prev_answer or not curr_question:
            continue
        checks += 1
        prev_tokens = {tok for tok in prev_answer.split() if len(tok) > 3}
        curr_tokens = {tok for tok in curr_question.split() if len(tok) > 3}
        if prev_tokens & curr_tokens:
            hits += 1
    if checks == 0:
        return 0.0
    return hits / checks


def generic_pattern_penalty(prediction: Dict[str, Any]) -> float:
    chain = prediction.get("why_chain") or []
    if not isinstance(chain, list) or not chain:
        return 1.0
    total = 0
    generic_hits = 0
    for step in chain:
        text = _safe_text((step or {}).get("answer"))
        if not text:
            continue
        total += 1
        if any(g in text for g in GENERIC_PATTERNS):
            generic_hits += 1
    if total == 0:
        return 1.0
    # 1 iyi, 0 kötü
    return max(0.0, 1.0 - (generic_hits / total))


def system_level_root_cause_bonus(prediction: Dict[str, Any]) -> float:
    rc = _safe_text(prediction.get("root_cause"))
    if not rc:
        return 0.0
    system_words = [
        "sistem",
        "prosedür",
        "organizasyon",
        "yönetim",
        "policy",
        "process",
        "management",
        "system",
    ]
    return 1.0 if any(w in rc for w in system_words) else 0.0


def hse_5why_metric(prediction: Dict[str, Any]) -> float:
    continuity = chain_continuity_score(prediction)
    non_generic = generic_pattern_penalty(prediction)
    system_bonus = system_level_root_cause_bonus(prediction)
    # ağırlıklı birleşik skor
    return round((0.45 * continuity) + (0.35 * non_generic) + (0.20 * system_bonus), 4)

