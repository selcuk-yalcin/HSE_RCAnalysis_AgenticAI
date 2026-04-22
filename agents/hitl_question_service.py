"""
Dinamik HITL soru üretimi: disambiguation bankası + HybridInputProcessor + QuestionEngine
(knowledge_base taxonomy şablonları). Sabit frontend listesi yok.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from agents.hitl_disambiguation_bank import build_questions_for_causes

_HS_CODE_RE = re.compile(r"\b([ABCD][0-9]+\.[0-9]+)\b", re.IGNORECASE)


def extract_hs_codes(text: str) -> list[str]:
    if not text:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for m in _HS_CODE_RE.finditer(text):
        code = m.group(1).upper()
        if code not in seen:
            seen.add(code)
            out.append(code)
    return out


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{h}"


def _immediate_causes_from_payload(
    immediate_causes: list[dict] | None,
    root_cause_initial: str,
) -> list[dict]:
    if immediate_causes:
        return [c for c in immediate_causes if isinstance(c, dict)]
    codes = extract_hs_codes(root_cause_initial or "")
    return [{"code": c, "cause_tr": c} for c in codes[:5]]


def _taxonomy_gap_questions(full_text: str, max_categories: int = 4, per_cat: int = 2) -> list[dict]:
    # Local imports: hitl_test modülleri repo kökünden import edilir (api/main sys.path).
    from hitl_test.hybrid_input_processor import HybridInputProcessor
    from hitl_test.question_engine import QuestionEngine

    _, det = HybridInputProcessor().detect_input_level(full_text or "")
    missing = det.get("missing") or []
    if not missing:
        return []
    qe = QuestionEngine()
    out: list[dict] = []
    for cat in missing[:max_categories]:
        rows = qe.generate_questions_for_missing_categories([cat])
        for i, row in enumerate(rows[:per_cat]):
            qtext = row.get("question") or ""
            if not qtext:
                continue
            hid = _stable_id("kb", cat, str(i), qtext)
            out.append(
                {
                    "id": hid,
                    "source": "taxonomy_gap",
                    "code": "",
                    "cause_desc": row.get("category_description", cat),
                    "hsg245": row.get("hsg245_link") or row.get("hsg245_codes", ""),
                    "soru": qtext,
                    "yönler": {},
                    "category": cat,
                    "required": bool(row.get("required")),
                }
            )
    return out


def build_hitl_question_pool(
    how_happened: str,
    root_cause_initial: str,
    immediate_causes: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """
    API + Gradio için tek havuz: önce immediate cause disambiguation, sonra eksik kategori soruları.
    """
    causes = _immediate_causes_from_payload(immediate_causes, root_cause_initial or "")
    disamb_raw = build_questions_for_causes(causes)
    pool: list[dict[str, Any]] = []
    seen_q: set[str] = set()

    for row in disamb_raw:
        soru = row.get("soru") or ""
        if not soru or soru.lower() in seen_q:
            continue
        seen_q.add(soru.lower())
        code = row.get("code", "")
        qid = _stable_id("d", code, soru)
        pool.append(
            {
                "id": qid,
                "source": "disambiguation",
                "code": code,
                "cause_desc": row.get("cause_desc", code),
                "hsg245": row.get("hsg245", ""),
                "soru": soru,
                "yönler": row.get("yönler") or {},
            }
        )

    full_text = "\n\n".join(
        s for s in (how_happened or "", root_cause_initial or "") if s.strip()
    )
    for row in _taxonomy_gap_questions(full_text):
        soru = row.get("soru") or ""
        if not soru or soru.lower() in seen_q:
            continue
        seen_q.add(soru.lower())
        pool.append(row)

    return pool[:20]


def next_hitl_questions(
    how_happened: str,
    root_cause_initial: str,
    answered_ids: list[str],
    immediate_causes: list[dict] | None = None,
    batch_size: int = 1,
) -> dict[str, Any]:
    """
    Cevaplanmış id'leri düşürür; sıradaki batch_size soruyu döndürür.
    """
    answered = set(answered_ids or [])
    pool = build_hitl_question_pool(how_happened, root_cause_initial, immediate_causes)
    pending = [q for q in pool if q.get("id") not in answered]
    batch = pending[: max(1, batch_size)]

    def _shape(q: dict) -> dict[str, Any]:
        return {
            "id": q["id"],
            "source": q.get("source", "disambiguation"),
            "hsg_hint": q.get("hsg245", ""),
            "code": q.get("code", ""),
            "cause_desc": q.get("cause_desc", ""),
            "question_tr": q.get("soru", ""),
            "question_en": q.get("soru", ""),
            "yönler": q.get("yönler") or {},
        }

    return {
        "questions": [_shape(q) for q in batch],
        "total_pool": len(pool),
        "remaining_after_batch": max(0, len(pending) - len(batch)),
        "done": len(pending) == 0,
    }


def build_why_probe_question_pool(
    how_happened: str,
    root_cause_initial: str,
    immediate_code: str = "",
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
) -> list[dict[str, Any]]:
    """
    Why zinciri içinde ara netleştirme soruları üretir.

    Sıra:
      1) Immediate code için disambiguation
      2) Code-specific taxonomy soruları
      3) Eksik bilgi kategorileri (HybridInputProcessor + QuestionEngine)
    """
    from hitl_test.question_engine import QuestionEngine

    focus_codes: list[str] = []
    if immediate_code:
        focus_codes.append(immediate_code.upper())
    for code in extract_hs_codes("\n".join([root_cause_initial or "", current_why_question or ""])):
        if code not in focus_codes:
            focus_codes.append(code)
    focus_codes = focus_codes[:3]

    pool: list[dict[str, Any]] = []
    seen_q: set[str] = set()

    # 1) Disambiguation (hedef immediate code)
    if focus_codes:
        causes = [{"code": c, "cause_tr": c} for c in focus_codes]
        for row in build_questions_for_causes(causes)[:4]:
            soru = row.get("soru") or ""
            if not soru or soru.lower() in seen_q:
                continue
            seen_q.add(soru.lower())
            qid = _stable_id("wp-d", str(why_level), row.get("code", ""), soru)
            pool.append(
                {
                    "id": qid,
                    "source": "why_probe_disambiguation",
                    "code": row.get("code", ""),
                    "cause_desc": row.get("cause_desc", ""),
                    "hsg245": row.get("hsg245", ""),
                    "soru": soru,
                    "yönler": row.get("yönler") or {},
                    "why_level": why_level,
                }
            )

    # 2) Code-specific questions (knowledge_base bağlı template'ler)
    qe = QuestionEngine()
    for i, row in enumerate(qe.get_code_specific_questions(focus_codes)[:6]):
        soru = row.get("question") or ""
        code = row.get("hsg245_code", "")
        if not soru or soru.lower() in seen_q:
            continue
        seen_q.add(soru.lower())
        qid = _stable_id("wp-c", str(why_level), code, str(i), soru)
        pool.append(
            {
                "id": qid,
                "source": "why_probe_code_specific",
                "code": code,
                "cause_desc": row.get("code_description", ""),
                "hsg245": code,
                "soru": soru,
                "yönler": {},
                "why_level": why_level,
            }
        )

    # 3) Gap questions (kontekst eksikleri)
    full_text = "\n\n".join(
        s
        for s in (
            how_happened or "",
            root_cause_initial or "",
            current_why_question or "",
            previous_why_answer or "",
        )
        if s.strip()
    )
    for row in _taxonomy_gap_questions(full_text, max_categories=2, per_cat=1):
        soru = row.get("soru") or ""
        if not soru or soru.lower() in seen_q:
            continue
        seen_q.add(soru.lower())
        row["id"] = _stable_id("wp-kb", str(why_level), row["id"], soru)
        row["source"] = "why_probe_taxonomy_gap"
        row["why_level"] = why_level
        pool.append(row)

    return pool[:12]


def next_why_probe_questions(
    how_happened: str,
    root_cause_initial: str,
    answered_ids: list[str],
    immediate_code: str = "",
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
    batch_size: int = 1,
) -> dict[str, Any]:
    """
    Why-level ara sorular: her seviyede daha net sebep ayrımı için döngüsel API.
    """
    answered = set(answered_ids or [])
    pool = build_why_probe_question_pool(
        how_happened=how_happened,
        root_cause_initial=root_cause_initial,
        immediate_code=immediate_code,
        why_level=why_level,
        current_why_question=current_why_question,
        previous_why_answer=previous_why_answer,
    )
    pending = [q for q in pool if q.get("id") not in answered]
    batch = pending[: max(1, batch_size)]

    def _shape(q: dict) -> dict[str, Any]:
        return {
            "id": q["id"],
            "source": q.get("source", "why_probe"),
            "hsg_hint": q.get("hsg245", ""),
            "code": q.get("code", ""),
            "cause_desc": q.get("cause_desc", ""),
            "question_tr": q.get("soru", ""),
            "question_en": q.get("soru", ""),
            "yönler": q.get("yönler") or {},
            "why_level": q.get("why_level", why_level),
        }

    return {
        "questions": [_shape(q) for q in batch],
        "total_pool": len(pool),
        "remaining_after_batch": max(0, len(pending) - len(batch)),
        "done": len(pending) == 0,
    }
