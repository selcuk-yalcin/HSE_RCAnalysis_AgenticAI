"""
Dinamik HITL soru üretimi: disambiguation bankası + HybridInputProcessor + QuestionEngine
(knowledge_base taxonomy şablonları). Sabit frontend listesi yok.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from agents.hitl_disambiguation_bank import build_questions_for_causes
from agents.hgs_taxonomy import parse_hsg_taxonomy_items, infer_codes_from_text

_HS_CODE_RE = re.compile(r"\b([ABCD][0-9]+\.[0-9]+)\b", re.IGNORECASE)
_GENERIC_PATTERNS = (
    "olay hangi tarih ve saatte",
    "risk değerlendirmesi yapılmış mıydı",
    "risk degerlendirmesi yapilmis miydi",
)

_KNOWN_FIELD_GUARD_PATTERNS = {
    "risk_assessment": (r"risk\s+de[ğg]erlendirmesi",),
    "timeline_known": (r"hangi\s+tarih", r"hangi\s+saat", r"ne\s+zaman"),
    "training_known": (r"e[ğg]itim", r"sertifika", r"yetki belgesi"),
    "ppe_known": (r"\bkkd\b", r"\bppe\b"),
    "permit_known": (r"i[sş]\s+izni", r"\bptw\b", r"permit"),
    "weather_known": (r"hava\s+ko[şs]ullar", r"ya[ğg]mur|r[üu]zgar|s[ıi]cak"),
    "lighting_known": (r"ayd[ıi]nlatma",),
}

try:
    _TAXONOMY_ITEMS = parse_hsg_taxonomy_items("agents/knowledge.json")
except Exception:
    _TAXONOMY_ITEMS = []


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
    if not codes:
        # fallback: derive candidate codes from first immediate-cause lines
        lines = [
            re.sub(r"^\s*\d+[\.)-]?\s*", "", ln).strip()
            for ln in str(root_cause_initial or "").splitlines()
            if ln.strip()
        ][:6]
        for ln in lines:
            for c in infer_codes_from_text(ln, _TAXONOMY_ITEMS, top_k=2):
                if c not in codes:
                    codes.append(c)
    return [{"code": c, "cause_tr": c} for c in codes[:5]]


def _build_deep_questions_from_taxonomy(code: str, why_level: int) -> list[dict]:
    if not code or not _TAXONOMY_ITEMS:
        return []
    item = next((x for x in _TAXONOMY_ITEMS if x.code == code), None)
    if item is None:
        return []

    out: list[dict] = []
    # Prefer "choose_if" lines as targeted disambiguation probes.
    for idx, choose in enumerate(item.choose_if[:2], start=1):
        q = f"{item.code} ({item.title}) icin: {choose} Bu olayda sahaya ne kadar uyuyordu?"
        out.append(
            {
                "id": _stable_id("tx-c", code, str(why_level), str(idx), q),
                "source": "why_probe_taxonomy_code",
                "code": item.code,
                "cause_desc": item.title,
                "hsg245": item.code,
                "soru": q,
                "yönler": {},
                "why_level": why_level,
            }
        )
    # One deepening question from "not this if" to reduce wrong mapping.
    if item.not_this_if:
        nt = item.not_this_if[0]
        q = f"Bu durum `{item.code}` yerine `{nt}` olabilir mi? Ayirmamiza yardim edecek kanit var mi?"
        out.append(
            {
                "id": _stable_id("tx-n", code, str(why_level), q),
                "source": "why_probe_taxonomy_code",
                "code": item.code,
                "cause_desc": item.title,
                "hsg245": item.code,
                "soru": q,
                "yönler": {},
                "why_level": why_level,
            }
        )
    return out


def _filter_questions(
    questions: list[dict[str, Any]],
    known_fields: list[str] | None,
) -> list[dict[str, Any]]:
    known = {str(k or "").strip().lower() for k in (known_fields or []) if str(k or "").strip()}
    out: list[dict[str, Any]] = []
    for q in questions:
        text = str(q.get("soru") or "").strip()
        if not text:
            continue
        low = text.lower()
        if any(p in low for p in _GENERIC_PATTERNS):
            continue
        skip = False
        for field in known:
            for patt in _KNOWN_FIELD_GUARD_PATTERNS.get(field, ()):
                if re.search(patt, low, flags=re.IGNORECASE):
                    skip = True
                    break
            if skip:
                break
        if not skip:
            out.append(q)
    return out


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
    known_fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Cevaplanmış id'leri düşürür; sıradaki batch_size soruyu döndürür.
    """
    answered = set(answered_ids or [])
    pool = _filter_questions(
        build_hitl_question_pool(how_happened, root_cause_initial, immediate_causes),
        known_fields=known_fields,
    )
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
    known_fields: list[str] | None = None,
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

    # 1) Code-grounded deep questions directly from taxonomy item.
    for code in focus_codes:
        for row in _build_deep_questions_from_taxonomy(code, why_level):
            soru = row.get("soru") or ""
            if not soru or soru.lower() in seen_q:
                continue
            seen_q.add(soru.lower())
            pool.append(row)

    # 2) Disambiguation (hedef immediate code)
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

    # 3) Code-specific questions (knowledge_base bağlı template'ler)
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

    return _filter_questions(pool[:14], known_fields=known_fields)


def next_why_probe_questions(
    how_happened: str,
    root_cause_initial: str,
    answered_ids: list[str],
    immediate_code: str = "",
    why_level: int = 1,
    current_why_question: str = "",
    previous_why_answer: str = "",
    batch_size: int = 1,
    known_fields: list[str] | None = None,
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
        known_fields=known_fields,
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
