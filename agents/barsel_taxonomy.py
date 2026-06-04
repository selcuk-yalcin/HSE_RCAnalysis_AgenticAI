"""
BARSEL taksonomi loader + HITL yardımcıları.

Kaynak: rag_pipeline/data/processed/barsel_taxonomy_multilingual.json
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from rag_pipeline.indexing.barsel_rag_document import parse_keywords

_TOKEN_RE = re.compile(r"[a-z0-9çğıöşü]+", re.IGNORECASE)
_CODE_RE = re.compile(r"\b([ABCD]\d+\.\d+)\b", re.IGNORECASE)
_DEFAULT_JSON = (
    Path(__file__).resolve().parent.parent
    / "rag_pipeline/data/processed/barsel_taxonomy_multilingual.json"
)

_ALL: List["BarselTaxonomyItem"] = []
_BY_CODE: Dict[str, "BarselTaxonomyItem"] = {}
_BAND: Dict[str, List["BarselTaxonomyItem"]] = {"A": [], "B": [], "C": [], "D": []}
_INDEX_LOADED = False


@dataclass
class BarselTaxonomyItem:
    code: str
    title: str
    definition: str = ""
    selection_criteria: str = ""
    typical_problems: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    section_ids: List[str] = field(default_factory=list)
    related_codes: List[str] = field(default_factory=list)
    cause_type: str = ""

    def to_search_text(self) -> str:
        parts = [
            self.code,
            self.title,
            self.definition,
            self.selection_criteria,
            " ".join(self.keywords),
            " ".join(self.typical_problems),
        ]
        return " ".join(p for p in parts if p).lower()


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or "") if len(t) >= 3}


def load_barsel_taxonomy_items(
    json_path: Optional[str] = None,
) -> List[BarselTaxonomyItem]:
    path = Path(json_path or os.getenv("BARSEL_TAXONOMY_JSON") or _DEFAULT_JSON)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    causes = data.get("causes") or []
    items: List[BarselTaxonomyItem] = []
    for raw in causes:
        if not isinstance(raw, dict):
            continue
        code = str(raw.get("code") or "").strip().upper()
        if not code:
            continue
        tr = (raw.get("content") or {}).get("tr") or {}
        kw_raw = (raw.get("keywords") or {}).get("tr") or []
        keywords: List[str] = []
        if isinstance(kw_raw, list):
            for entry in kw_raw:
                keywords.extend(parse_keywords(entry))
        keywords = list(dict.fromkeys(k for k in keywords if k))
        probs = tr.get("typical_problems") or []
        if not isinstance(probs, list):
            probs = []
        items.append(
            BarselTaxonomyItem(
                code=code,
                title=str(tr.get("title") or code),
                definition=str(tr.get("definition") or ""),
                selection_criteria=str(tr.get("selection_criteria") or "").strip(),
                typical_problems=[str(p).strip() for p in probs if str(p).strip()],
                keywords=keywords,
                section_ids=[str(s) for s in (raw.get("section_ids") or [])],
                related_codes=[str(c).upper() for c in (raw.get("related_codes") or []) if c],
                cause_type=str(raw.get("cause_type") or ""),
            )
        )
    return items


def barsel_taxonomy_enabled() -> bool:
    """Production varsayılan: BARSEL. Eski HSG: ROOTCAUSE_TAXONOMY_SOURCE=hsg"""
    src = (os.getenv("ROOTCAUSE_TAXONOMY_SOURCE") or "barsel").strip().lower()
    return src not in ("hsg", "hsg245", "knowledge_json", "knowledge")


def taxonomy_prompt_mode() -> str:
    """
    rag — Mongo taxonomy_barsel retriever (varsayılan, olay-özel)
    static — tüm band JSON listesi
    auto — retriever bağlıysa rag, değilse static compact
    """
    return (os.getenv("ROOTCAUSE_TAXONOMY_MODE") or "rag").strip().lower()


def _taxonomy_rag_k() -> int:
    try:
        return max(3, min(20, int(os.getenv("ROOTCAUSE_TAXONOMY_RAG_K") or "8")))
    except ValueError:
        return 8


def _static_max_codes() -> int:
    try:
        return max(5, min(40, int(os.getenv("ROOTCAUSE_TAXONOMY_STATIC_MAX") or "12")))
    except ValueError:
        return 12


def _ensure_index() -> None:
    global _INDEX_LOADED, _ALL, _BY_CODE, _BAND
    if _INDEX_LOADED:
        return
    _INDEX_LOADED = True
    _ALL = load_barsel_taxonomy_items()
    _BY_CODE = {i.code.upper(): i for i in _ALL if i.code}
    for band in _BAND:
        _BAND[band] = sorted(
            [i for i in _ALL if (i.code or "").upper().startswith(band)],
            key=lambda x: x.code,
        )


def extract_taxonomy_code(raw: Optional[str]) -> str:
    if not raw or not str(raw).strip():
        return ""
    s = re.sub(r"\s+", " ", str(raw).strip().upper())
    s_compact = s.replace(" ", "")
    m = _CODE_RE.search(s_compact)
    if m:
        return m.group(1).upper()
    m2 = re.search(r"([ABCD])\s*(\d+)\s*\.\s*(\d+)", s)
    if m2:
        return f"{m2.group(1).upper()}{m2.group(2)}.{m2.group(3)}"
    return s_compact if re.match(r"^[ABCD]\d+\.\d+$", s_compact) else ""


def get_barsel_category_prompt(
    category: str,
    *,
    include_definition: bool = True,
    max_codes: Optional[int] = None,
) -> str:
    """DSPy prompt için A/B/C/D band kod listesi (statik JSON)."""
    _ensure_index()
    if not _ALL:
        return ""
    cat = (category or "").upper()
    labels = {
        "A": "A band — davranışsal doğrudan nedenler",
        "B": "B band — koşul/ortam doğrudan nedenler",
        "C": "C band — kişisel kök nedenler",
        "D": "D band — organizasyonel kök nedenler",
        "AB": "A + B — doğrudan nedenler (davranış + koşul)",
        "CD": "C + D — kök nedenler (kişisel + organizasyonel)",
    }
    if cat == "AB":
        items = _BAND["A"] + _BAND["B"]
    elif cat == "CD":
        items = _BAND["C"] + _BAND["D"]
    elif cat in _BAND:
        items = _BAND[cat]
    else:
        return ""
    if max_codes is not None and len(items) > max_codes:
        items = items[:max_codes]
    lines = [f"BARSEL TAKSONOMİ (statik) — {labels.get(cat, cat)}:", ""]
    for item in items:
        row = f"{item.code} {item.title}"
        if include_definition and item.definition:
            short = re.sub(r"\s+", " ", item.definition)[:200]
            row += f" — {short}"
        lines.append(row)
    return "\n".join(lines)


def format_retrieval_hits_prompt(
    hits: List[Dict],
    header: str,
) -> str:
    """Mongo RAG hit listesini DSPy taxonomy_codes metnine çevir."""
    if not hits:
        return ""
    lines = [header, ""]
    for h in hits:
        tr = (h.get("content") or {}).get("tr") or {}
        title = tr.get("title") or h.get("code") or ""
        defn = (tr.get("definition") or "")[:200]
        probs = tr.get("typical_problems") or []
        prob = (probs[0] or "")[:120] if probs else ""
        row = f"{h.get('code')} {title}"
        if defn:
            row += f" — {defn}"
        if prob:
            row += f" | Tipik: {prob}"
        kw = h.get("keywords")
        if isinstance(kw, list) and kw:
            row += f" | Anahtar: {', '.join(str(k) for k in kw[:4])}"
        lines.append(row)
    return "\n".join(lines)


def retrieve_band_taxonomy_prompt(
    query: str,
    band: str,
    retriever: Any,
    *,
    k: Optional[int] = None,
) -> str:
    """Mongo taxonomy_barsel — iki aşamalı retriever, band filtresi."""
    if retriever is None or not getattr(retriever, "connected", False):
        return ""
    band = (band or "").upper()
    labels = {
        "A": "A band — davranışsal doğrudan nedenler",
        "B": "B band — koşul/ortam doğrudan nedenler",
        "C": "C band — kişisel kök nedenler",
        "D": "D band — organizasyonel kök nedenler",
    }
    if band not in labels:
        return ""
    top_k = k or _taxonomy_rag_k()
    hits = retriever.retrieve(
        (query or "")[:4000],
        k=top_k,
        band=band,
        min_score=0.02,
        keyword_pool=max(20, top_k * 3),
    )
    if not hits:
        return ""
    return format_retrieval_hits_prompt(
        hits,
        f"BARSEL RAG (Mongo) — {labels[band]} — olayla en ilgili {len(hits)} kod:",
    )


def get_incident_taxonomy_prompt(
    category: str,
    query: str,
    retriever: Any = None,
) -> str:
    """
    Olay metnine göre taksonomi prompt'u.
    Varsayılan: Mongo RAG (ucuz + çeşitli). Fallback: statik JSON (kısaltılmış).
    """
    if not barsel_taxonomy_enabled():
        try:
            from agents.knowledge_base import get_category_text

            return get_category_text(category)
        except ImportError:
            return ""

    mode = taxonomy_prompt_mode()
    use_rag = mode == "rag" or (
        mode == "auto"
        and retriever is not None
        and getattr(retriever, "connected", False)
    )
    cat = (category or "").upper()
    static_max = _static_max_codes()

    if use_rag and retriever is not None:
        if cat in ("A", "B", "C", "D"):
            rag_text = retrieve_band_taxonomy_prompt(query, cat, retriever)
            if rag_text:
                return rag_text
        elif cat == "AB":
            a = retrieve_band_taxonomy_prompt(query, "A", retriever)
            b = retrieve_band_taxonomy_prompt(query, "B", retriever)
            parts = [p for p in (a, b) if p]
            if parts:
                return "\n\n".join(parts)
        elif cat == "CD":
            c = retrieve_band_taxonomy_prompt(query, "C", retriever, k=max(4, _taxonomy_rag_k() // 2))
            d = retrieve_band_taxonomy_prompt(query, "D", retriever, k=_taxonomy_rag_k())
            parts = [p for p in (c, d) if p]
            if parts:
                return "\n\n".join(parts)

    return get_barsel_category_prompt(
        cat,
        include_definition=True,
        max_codes=static_max,
    )


def get_taxonomy_category_text(category: str) -> str:
    """Statik band metni (incident yok — BranchCritic init vb.)."""
    if barsel_taxonomy_enabled():
        return get_barsel_category_prompt(
            category,
            include_definition=False,
            max_codes=_static_max_codes(),
        )
    try:
        from agents.knowledge_base import get_category_text

        return get_category_text(category)
    except ImportError:
        return ""


def _category_type_label(code: str) -> str:
    letter = (code or "").upper()[:1]
    if letter == "C":
        return "KİŞİSEL"
    if letter == "D":
        return "ORGANİZASYONEL"
    if letter in ("A", "B"):
        return letter
    return "ORGANİZASYONEL"


def snap_to_barsel_taxonomy(
    code: str,
    model_answer: str,
    base_explanation: str,
    *,
    family: str = "cd",
) -> Optional[Dict[str, str]]:
    """
    LLM çıktısını BARSEL resmi kod + başlığa hizala (Why-5 / meta kök neden).
    family: 'cd' = C+D; 'd' = yalnız D.
    """
    _ensure_index()
    if family in ("d", "D"):
        pool = _BAND["D"]
    else:
        pool = _BAND["C"] + _BAND["D"]
    if not pool:
        return None

    by_code = {i.code.upper(): i for i in pool}
    narrative = (model_answer or "").strip()
    code_guess = extract_taxonomy_code(code)
    if code_guess and code_guess not in by_code:
        code_guess = ""
    item: Optional[BarselTaxonomyItem] = by_code.get(code_guess) if code_guess else None
    if not item and narrative:
        inferred = infer_barsel_codes_from_text(narrative, pool, top_k=1)
        if inferred:
            item = by_code.get(inferred[0].upper())
    if not item and (code or "").strip():
        for ic in infer_barsel_codes_from_text(f"{code}\n{narrative}", pool, top_k=1):
            item = by_code.get(ic.upper())
            if item:
                break
    if not item:
        return None

    try:
        from agents.report_text_sanitize import sanitize_report_text, taxonomy_display_title
    except ImportError:
        from .report_text_sanitize import sanitize_report_text, taxonomy_display_title

    cause_tr = taxonomy_display_title(
        item.code,
        item.title,
        sanitize_report_text(narrative),
    )
    explanation_tr = sanitize_report_text((base_explanation or "").strip())
    if not explanation_tr:
        explanation_tr = sanitize_report_text(narrative)
    return {
        "code": item.code,
        "cause_tr": cause_tr,
        "category_type": _category_type_label(item.code),
        "explanation_tr": explanation_tr,
    }


def snap_immediate_cause_to_barsel(cause: Dict) -> Dict:
    """A/B doğrudan neden satırını BARSEL kod + resmi başlığa hizala."""
    _ensure_index()
    if not barsel_taxonomy_enabled() or not _ALL:
        return cause
    pool = _BAND["A"] + _BAND["B"]
    if not pool:
        return cause

    by_code = {i.code.upper(): i for i in pool}
    raw_code = str(cause.get("code") or "").strip().upper()
    narrative = str(cause.get("cause_tr") or "").strip()
    code_guess = extract_taxonomy_code(raw_code) or raw_code
    item = by_code.get(code_guess) if code_guess else None
    if not item and narrative:
        inferred = infer_barsel_codes_from_text(
            f"{raw_code}\n{narrative}", pool, top_k=1
        )
        if inferred:
            item = by_code.get(inferred[0].upper())
    if not item:
        return cause

    out = dict(cause)
    out["code"] = item.code
    out["standard_title_tr"] = item.title
    out["category_type"] = (item.code or "")[:1]
    return out


def infer_barsel_codes_from_text(
    text: str,
    items: Iterable[BarselTaxonomyItem],
    top_k: int = 3,
) -> List[str]:
    qtokens = _tokenize(text)
    if not qtokens:
        return []
    scored: List[tuple[float, str]] = []
    for item in items:
        stokens = _tokenize(item.to_search_text())
        if not stokens:
            continue
        common = qtokens.intersection(stokens)
        if not common:
            continue
        kw_tokens = _tokenize(" ".join(item.keywords))
        kw_bonus = len(qtokens.intersection(kw_tokens)) * 0.5
        score = len(common) / max(1.0, len(qtokens)) + kw_bonus
        scored.append((score, item.code))
    scored.sort(key=lambda x: x[0], reverse=True)
    out: List[str] = []
    for _, code in scored:
        if code not in out:
            out.append(code)
        if len(out) >= top_k:
            break
    return out


def split_selection_criteria(text: str, max_clauses: int = 2) -> List[str]:
    raw = (text or "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in re.split(r"\s+/\s+|(?<=[.!?])\s+", raw) if p.strip()]
    if not parts:
        parts = [raw]
    return parts[:max_clauses]


def keyword_overlap_score(text_a: str, text_b: str) -> float:
    a = _tokenize(text_a)
    b = _tokenize(text_b)
    if not a or not b:
        return 0.0
    return len(a.intersection(b)) / len(a.union(b))


def pick_typical_problems_for_hitl(
    item: BarselTaxonomyItem,
    incident_text: str,
    why_level: int,
    *,
    max_problems: int = 2,
) -> List[str]:
    probs = [p for p in item.typical_problems if p.strip()]
    if not probs:
        return []
    incident = incident_text or ""

    def rank_key(problem: str) -> tuple[float, str]:
        overlap = keyword_overlap_score(incident, problem)
        kw_overlap = keyword_overlap_score(incident, " ".join(item.keywords))
        return (overlap + 0.35 * kw_overlap, problem)

    ranked = sorted(probs, key=rank_key, reverse=True)
    start = (max(1, why_level) - 1) % len(ranked)
    rotated = ranked[start:] + ranked[:start]
    return rotated[:max_problems]


def find_contrast_code(
    item: BarselTaxonomyItem,
    items: Iterable[BarselTaxonomyItem],
) -> Optional[BarselTaxonomyItem]:
    if item.related_codes:
        rel = item.related_codes[0].upper()
        for other in items:
            if other.code == rel:
                return other
    band = item.section_ids[-1] if item.section_ids else item.code.rsplit(".", 1)[0]
    siblings = [
        o
        for o in items
        if o.code != item.code
        and (band in o.section_ids or o.code.startswith(f"{band}."))
    ]
    if not siblings:
        return None
    siblings.sort(key=lambda o: abs(len(o.code) - len(item.code)))
    return siblings[0]
