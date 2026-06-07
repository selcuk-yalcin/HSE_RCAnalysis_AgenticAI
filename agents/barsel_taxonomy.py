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
    section_titles: List[str] = field(default_factory=list)
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
                section_titles=[
                    str(t).strip() for t in (raw.get("section_titles") or []) if str(t).strip()
                ],
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


def normalize_taxonomy_title(title: str) -> str:
    """BARSEL tr.title öneklerini (—, tire) temizle."""
    t = re.sub(r"\s+", " ", str(title or "").strip())
    t = re.sub(r"^[—–\-]+\s*", "", t)
    return t.strip()


def official_title_tr_for_code(code: str) -> str:
    """Rapor/HITL için resmi Türkçe yaprak başlık (CODE_TITLE_TR → barsel JSON)."""
    key = (code or "").strip().upper()
    if not key:
        return ""
    try:
        from agents.taxonomy_title_tr_map import CODE_TITLE_TR
    except ImportError:
        from .taxonomy_title_tr_map import CODE_TITLE_TR
    if key in CODE_TITLE_TR:
        return CODE_TITLE_TR[key]
    _ensure_index()
    item = _BY_CODE.get(key)
    if not item:
        return ""
    try:
        from agents.taxonomy_title_tr_map import normalize_display_title
    except ImportError:
        from .taxonomy_title_tr_map import normalize_display_title
    return normalize_display_title(normalize_taxonomy_title(item.title))


def section_titles_tr_for_code(code: str) -> List[str]:
    """Üst bölüm başlıkları (ör. D8. SATIN ALMA, MALZEME TAŞIMA...)."""
    key = (code or "").strip().upper()
    if not key:
        return []
    _ensure_index()
    item = _BY_CODE.get(key)
    if item and item.section_titles:
        return [normalize_taxonomy_title(t) for t in item.section_titles if str(t).strip()]
    gid = group_id_from_code(key)
    if gid:
        parent = _BY_CODE.get(gid)
        if parent and parent.section_titles:
            return [normalize_taxonomy_title(t) for t in parent.section_titles if str(t).strip()]
    return []


def group_id_from_code(code: str) -> str:
    """D8.4 → D8, C3.2 → C3."""
    m = re.match(r"^([CD]\d+)", (code or "").strip().upper())
    return m.group(1) if m else ""


def _strip_group_code_prefix(section_title: str, code: str) -> str:
    """'D8. SATIN ALMA...' → 'SATIN ALMA...' (rapor başlığı)."""
    t = normalize_taxonomy_title(section_title)
    gid = group_id_from_code(code)
    if gid:
        t = re.sub(rf"^{re.escape(gid)}\.?\s*", "", t, flags=re.IGNORECASE).strip()
    return t


def critical_factor_title_for_code(code: str) -> str:
    """
    Kritik Faktör başlığı: C1 / D4 / D8 ana grup (kodsuz).
    Örn. D8.4 → 'SATIN ALMA, MALZEME TAŞIMA VE MALZEME KONTROLÜ'
    Örn. D4.3 → 'RİSK VE İŞ KONTROL SİSTEMLERİ'
    """
    key = (code or "").strip().upper()
    if not key or key[0] not in ("C", "D"):
        return ""
    try:
        from agents.taxonomy_title_tr_map import group_title_tr_for_code
    except ImportError:
        from .taxonomy_title_tr_map import group_title_tr_for_code

    mapped = group_title_tr_for_code(key)
    if mapped:
        return mapped

    trail = section_titles_tr_for_code(key)
    if len(trail) >= 2:
        return _strip_group_code_prefix(trail[-1], key)
    if trail:
        return _strip_group_code_prefix(trail[0], key)
    gid = group_id_from_code(key)
    if gid:
        _ensure_index()
        parent = _BY_CODE.get(gid)
        if parent:
            return normalize_taxonomy_title(parent.title)
    return ""


def resolve_root_cause_code_from_branch(branch: Optional[Dict[str, Any]]) -> str:
    """analysis_branches / rapor dalından C/D kök neden kodu çıkar."""
    if not isinstance(branch, dict):
        return ""
    root = branch.get("root_cause") if isinstance(branch.get("root_cause"), dict) else {}
    for src in (
        str((root or {}).get("code") or ""),
        str((root or {}).get("standard_title_tr") or ""),
        str((root or {}).get("cause_tr") or ""),
        str(branch.get("root_cause_title") or ""),
    ):
        code = extract_taxonomy_code(src)
        if code and code[0] in ("C", "D"):
            return code
    why_chain = branch.get("why_chain") or branch.get("questions_and_answers") or []
    if isinstance(why_chain, list):
        for w in reversed(why_chain):
            if not isinstance(w, dict):
                continue
            for field in ("code", "answer_tr", "answer", "question_tr", "question"):
                code = extract_taxonomy_code(str(w.get(field) or ""))
                if code and code[0] in ("C", "D"):
                    return code
    return ""


def _raw_branch_lookup(
    raw_branches: List[Dict[str, Any]],
    branch_number: Any,
    index: int,
) -> Dict[str, Any]:
    """branch_number ile ham RCA dalını eşleştir (LLM sıra kaymasına dayanıklı)."""
    if not raw_branches:
        return {}
    by_num: Dict[Any, Dict[str, Any]] = {}
    for i, rb in enumerate(raw_branches):
        if not isinstance(rb, dict):
            continue
        bn = rb.get("branch_number") or (i + 1)
        by_num[bn] = rb
        by_num[i + 1] = rb
    if branch_number in by_num:
        return by_num[branch_number]
    if index < len(raw_branches) and isinstance(raw_branches[index], dict):
        return raw_branches[index]
    return {}


def root_cause_leaf_title_for_code(code: str) -> str:
    """Kök neden kutusu başlığı: yaprak kod title (kodsuz). Örn. D8.4 → Malzeme depolama yetersizliği."""
    return official_title_tr_for_code(code) or ""


def apply_official_taxonomy_titles_to_report_branches(
    branches: List[Dict[str, Any]],
    raw_branches: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Rapor dallarında kritik faktör + kök neden başlıklarını BARSEL JSON'dan zorla.
    LLM veya legacy CODE_TITLE_TR kısaltmaları yerine tablodaki tam Türkçe isim (kodsuz).
    """
    raw_branches = raw_branches or []
    out: List[Dict[str, Any]] = []
    for i, branch in enumerate(branches or []):
        if not isinstance(branch, dict):
            out.append(branch)
            continue
        br = dict(branch)
        bn = br.get("branch_number") or (i + 1)
        raw = _raw_branch_lookup(raw_branches, bn, i)
        code = resolve_root_cause_code_from_branch(raw) or resolve_root_cause_code_from_branch(br)
        if code and code[0] in ("C", "D"):
            leaf = root_cause_leaf_title_for_code(code)
            cf = critical_factor_title_for_code(code)
            if leaf:
                br["root_cause_title"] = leaf
            if cf:
                br["branch_title"] = f"KRİTİK FAKTÖR {bn} - {cf}"
            br["root_cause_section"] = ""
        out.append(br)
    return out


def apply_official_taxonomy_titles_to_root_causes(
    root_causes: List[Dict[str, Any]],
    raw_branches: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Özet kök neden listesinde title/section alanlarını BARSEL ile hizala."""
    raw_branches = raw_branches or []
    out: List[Dict[str, Any]] = []
    for i, rc in enumerate(root_causes or []):
        if not isinstance(rc, dict):
            out.append(rc)
            continue
        row = dict(rc)
        bn = row.get("branch_number") or (i + 1)
        raw = _raw_branch_lookup(raw_branches, bn, i)
        code = (
            resolve_root_cause_code_from_branch(raw)
            or extract_taxonomy_code(str(row.get("code") or ""))
        )
        if code and code[0] in ("C", "D"):
            leaf = root_cause_leaf_title_for_code(code)
            cf = critical_factor_title_for_code(code)
            if leaf:
                row["title"] = leaf
            if cf:
                row["section"] = cf
        out.append(row)
    return out


def build_root_cause_explanation_from_taxonomy(
    item: BarselTaxonomyItem,
    *,
    incident_hint: str = "",
    affirmed_typical_problems: Optional[List[str]] = None,
) -> str:
    """definition + typical_problems ile kök neden açıklaması (rapor metni)."""
    try:
        from agents.why_chain_quality import demote_solution_to_cause
    except ImportError:
        from .why_chain_quality import demote_solution_to_cause

    parts: List[str] = []
    defn = demote_solution_to_cause((item.definition or "").strip())
    if defn:
        parts.append(defn)
    probs = affirmed_typical_problems or item.typical_problems or []
    for prob in probs[:2]:
        p = demote_solution_to_cause(str(prob).strip())
        if not p:
            continue
        if defn and p[:48] in defn:
            continue
        parts.append(p.rstrip("."))
    if incident_hint and len(" ".join(parts)) < 120:
        hint = demote_solution_to_cause(incident_hint[:280].strip())
        if hint:
            parts.append(f"Bu olay bağlamında: {hint}")
    return " ".join(parts).strip()


def enrich_root_cause_from_taxonomy(
    root: Dict,
    *,
    incident_hint: str = "",
    affirmed_typical_problems: Optional[List[str]] = None,
) -> Dict:
    """Kök neden dict'ini BARSEL definition/title ile hizala."""
    if not isinstance(root, dict):
        return root
    code = extract_taxonomy_code(str(root.get("code") or "")) or str(root.get("code") or "").strip().upper()
    if not code or code[0] not in ("C", "D"):
        return root
    _ensure_index()
    item = _BY_CODE.get(code)
    if not item:
        return root
    out = dict(root)
    leaf = root_cause_leaf_title_for_code(code)
    out["code"] = code
    if root.get("snap_rejected"):
        direct = str(root.get("cause_tr") or root.get("standard_title_tr") or "").strip()
        out["standard_title_tr"] = direct or leaf
        out["cause_tr"] = direct or leaf
    else:
        out["standard_title_tr"] = leaf
        out["cause_tr"] = leaf
    out["critical_factor_title"] = critical_factor_title_for_code(code)
    out["category_type"] = _category_type_label(code)
    narrative = str(root.get("explanation_tr") or root.get("cause_tr") or "").strip()
    tax_expl = build_root_cause_explanation_from_taxonomy(
        item,
        incident_hint=incident_hint or narrative,
        affirmed_typical_problems=affirmed_typical_problems,
    )
    out["explanation_tr"] = tax_expl or narrative
    return out


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
    cause_type_filter: Optional[str] = None,
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
        cause_type_filter=cause_type_filter,
        min_score=0.02,
        keyword_pool=max(20, top_k * 3),
    )
    if not hits:
        return ""
    return format_retrieval_hits_prompt(
        hits,
        f"BARSEL RAG (Mongo) — {labels[band]} — olayla en ilgili {len(hits)} kod:",
    )


def why_level_target_bands(why_level: int) -> List[str]:
    """RCA derinliği için band haritası (HITL probe artık band rotasyonu yapmaz)."""
    w = max(1, int(why_level or 1))
    if w <= 2:
        return ["A", "B"]
    if w <= 4:
        return ["C"]
    return ["D"]


def hitl_probe_min_relevance() -> float:
    raw = (os.getenv("HITL_PROBE_MIN_RELEVANCE") or "0.03").strip()
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return 0.03


def hitl_rag_min_score() -> float:
    raw = (os.getenv("HITL_RAG_MIN_SCORE") or "0.08").strip()
    try:
        return max(0.02, min(0.5, float(raw)))
    except ValueError:
        return 0.08


def item_relevance_score(item: BarselTaxonomyItem, incident_text: str) -> float:
    """Olay metni ↔ taksonomi öğesi benzerlik skoru."""
    incident = incident_text or ""
    base = keyword_overlap_score(incident, item.to_search_text())
    kw = keyword_overlap_score(incident, " ".join(item.keywords))
    return base + 0.35 * kw


def probe_context_relevance(
    probe_context: str,
    item: BarselTaxonomyItem,
    incident_text: str,
) -> float:
    """typical_problem / selection_criteria cümlesinin olayla örtüşmesi."""
    ctx = (probe_context or "").strip()
    if not ctx:
        return 0.0
    ctx_score = keyword_overlap_score(incident_text or "", ctx)
    item_score = item_relevance_score(item, incident_text)
    return max(ctx_score, item_score * 0.45)


def item_from_mongo_hit(hit: Dict[str, Any]) -> BarselTaxonomyItem:
    """Mongo taxonomy_barsel hit → BarselTaxonomyItem."""
    tr = (hit.get("content") or {}).get("tr") or {}
    kw_raw = hit.get("keywords") or []
    keywords: List[str] = []
    if isinstance(kw_raw, list):
        for entry in kw_raw:
            keywords.extend(parse_keywords(str(entry)))
    keywords = list(dict.fromkeys(k for k in keywords if k))
    probs = tr.get("typical_problems") or []
    if not isinstance(probs, list):
        probs = []
    return BarselTaxonomyItem(
        code=str(hit.get("code") or "").strip().upper(),
        title=str(tr.get("title") or hit.get("code") or ""),
        definition=str(tr.get("definition") or ""),
        selection_criteria=str(tr.get("selection_criteria") or "").strip(),
        typical_problems=[str(p).strip() for p in probs if str(p).strip()],
        keywords=keywords,
        section_ids=[str(s) for s in (hit.get("section_ids") or [])],
        section_titles=[
            str(t).strip() for t in (hit.get("section_titles") or []) if str(t).strip()
        ],
        cause_type=str(hit.get("cause_type") or ""),
    )


def retrieve_immediate_bands_prompt(
    query: str,
    retriever: Any,
    *,
    k_per_band: Optional[int] = None,
) -> str:
    """Mongo — cause_type immediate_cause, band A + B."""
    if retriever is None or not getattr(retriever, "connected", False):
        return ""
    q = (query or "")[:4000]
    if not q.strip():
        return ""
    per = k_per_band or max(3, _taxonomy_rag_k() // 2)
    parts: List[str] = []
    for band in ("A", "B"):
        hits = retriever.retrieve(
            q,
            k=per,
            band=band,
            cause_type_filter="immediate_cause",
            min_score=0.02,
            keyword_pool=max(15, per * 3),
        )
        if hits:
            parts.append(
                format_retrieval_hits_prompt(
                    hits,
                    f"BARSEL RAG (Mongo) — {band} doğrudan neden — olayla en ilgili {len(hits)} kod:",
                )
            )
    return "\n\n".join(parts).strip()


def codes_for_why_level(
    why_level: int,
    immediate_code: str,
    incident_text: str,
    retriever: Any,
    *,
    max_codes: int = 2,
) -> List[str]:
    """
    HITL dal-içi probe kodları.

    immediate_code bandında kalır; Why seviyesi A→C→D band rotasyonu yapmaz.
    """
    del why_level  # dal içi scope — seviye band değiştirmez
    imm = (immediate_code or "").strip().upper()
    if not imm:
        return []
    codes: List[str] = [imm]
    band = imm[0] if imm and imm[0] in "ABCD" else ""
    q = (incident_text or "")[:4000]
    min_rel = hitl_probe_min_relevance()

    _ensure_index()
    item = _BY_CODE.get(imm)
    if item:
        for rc in (item.related_codes or [])[:1]:
            rel = str(rc).strip().upper()
            if rel and rel not in codes and rel[0] == band:
                rel_item = _BY_CODE.get(rel)
                if rel_item and item_relevance_score(rel_item, q) >= min_rel:
                    codes.append(rel)

    if retriever is not None and getattr(retriever, "connected", False) and q.strip() and band:
        cause_filter = "immediate_cause" if band in ("A", "B") else "root_cause"
        hits = retriever.retrieve(
            q,
            k=max(1, max_codes),
            band=band,
            cause_type_filter=cause_filter,
            min_score=hitl_rag_min_score(),
            keyword_pool=12,
        )
        for h in hits:
            c = str(h.get("code") or "").strip().upper()
            if c and c not in codes and c.startswith(band):
                codes.append(c)

    if item and len(codes) < max_codes:
        section = item.section_ids[-1] if item.section_ids else group_id_from_code(imm)
        scored: List[tuple[float, str]] = []
        for sib in _BAND.get(band, []):
            if sib.code in codes:
                continue
            if section and not (
                section in sib.section_ids or sib.code.startswith(f"{section}.")
            ):
                continue
            score = item_relevance_score(sib, q)
            if score >= min_rel:
                scored.append((score, sib.code))
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, code in scored:
            codes.append(code)
            if len(codes) >= max_codes:
                break

    return codes[:max_codes]


def taxonomy_item_for_code(
    code: str,
    *,
    barsel_by_code: Optional[Dict[str, BarselTaxonomyItem]] = None,
    retriever: Any = None,
) -> Optional[BarselTaxonomyItem]:
    """JSON indeks veya Mongo bellek indeksinden tek kod."""
    key = (code or "").strip().upper()
    if not key:
        return None
    if barsel_by_code and key in barsel_by_code:
        return barsel_by_code[key]
    _ensure_index()
    if key in _BY_CODE:
        return _BY_CODE[key]
    r = retriever
    if r is not None and getattr(r, "connected", False):
        for doc in getattr(r, "_docs", []) or []:
            if str(doc.get("code") or "").strip().upper() == key:
                return item_from_mongo_hit(doc)
    return None


def probe_answer_affirms_fit(answer_text: str) -> bool:
    """HITL Evet/Hayır — kod uygunluğu onayı."""
    a = (answer_text or "").strip().lower()
    if not a:
        return False
    if a in ("yes", "evet", "true", "1"):
        return True
    if a in ("no", "hayır", "hayir", "false", "0", "unknown", "bilinmiyor", "skip", "geç", "gec"):
        return False
    return any(
        tok in a
        for tok in ("evet", "yes", "doğru", "dogru", "uygun", "geçerli", "gecerli")
    ) and not any(tok in a for tok in ("hayır", "hayir", "no", "değil", "degil"))


def build_definition_based_why_answer(
    item: BarselTaxonomyItem,
    *,
    question: str = "",
    incident_hint: str = "",
) -> str:
    """Probe onayı sonrası definition'dan geçmiş zamanlı Why cevabı."""
    try:
        from agents.why_chain_quality import demote_solution_to_cause, format_barsel_why_answer
    except ImportError:
        from .why_chain_quality import demote_solution_to_cause, format_barsel_why_answer

    body = demote_solution_to_cause((item.definition or item.title or "").strip())
    if incident_hint and len(body) < 40:
        body = f"{body} Olay bağlamında: {incident_hint[:200]}".strip()
    if not body:
        return ""
    return format_barsel_why_answer(item.code, body)


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

    immediate_only = (os.getenv("ROOTCAUSE_IMMEDIATE_MONGO_FILTER") or "1").strip().lower() in (
        "1", "true", "yes", "on",
    )
    imm_filter = "immediate_cause" if immediate_only else None

    if use_rag and retriever is not None:
        if cat in ("A", "B", "C", "D"):
            cf = imm_filter if cat in ("A", "B") else None
            rag_text = retrieve_band_taxonomy_prompt(
                query, cat, retriever, cause_type_filter=cf
            )
            if rag_text:
                return rag_text
        elif cat == "AB":
            a = retrieve_band_taxonomy_prompt(
                query, "A", retriever, cause_type_filter=imm_filter
            )
            b = retrieve_band_taxonomy_prompt(
                query, "B", retriever, cause_type_filter=imm_filter
            )
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

    leaf = root_cause_leaf_title_for_code(item.code) or normalize_taxonomy_title(item.title)
    explanation_tr = build_root_cause_explanation_from_taxonomy(
        item,
        incident_hint=sanitize_report_text((base_explanation or narrative or "").strip()),
    )
    if not explanation_tr:
        explanation_tr = sanitize_report_text((base_explanation or narrative or "").strip())
    return enrich_root_cause_from_taxonomy(
        {
            "code": item.code,
            "standard_title_tr": leaf,
            "cause_tr": leaf,
            "category_type": _category_type_label(item.code),
            "explanation_tr": explanation_tr,
        },
        incident_hint=narrative,
    )


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


def hitl_mongo_rag_enabled() -> bool:
    """HITL sorularında Mongo taxonomy_barsel retriever (varsayılan açık)."""
    if (os.getenv("HITL_USE_MONGO_RAG") or "1").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        return False
    if not barsel_taxonomy_enabled():
        return False
    return bool((os.getenv("MONGODB_URI") or "").strip())


def hitl_allow_legacy_fallback() -> bool:
    """Yerel JSON + HSG knowledge.json HITL yedeği (offline dev için)."""
    return (os.getenv("HITL_ALLOW_JSON_HSG_FALLBACK") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def hitl_mongo_only_sources() -> bool:
    """Mongo RAG açıkken JSON/HSG'den soru üretme (varsayılan)."""
    return hitl_mongo_rag_enabled() and not hitl_allow_legacy_fallback()


def _supplement_codes_from_retriever_docs(
    by_code: Dict[str, BarselTaxonomyItem],
    focus_codes: Iterable[str],
    retriever: Any,
) -> None:
    """Agent/RCA kodlarını retriever bellek indeksinden tamamla (JSON yedeği yok)."""
    if retriever is None or not getattr(retriever, "connected", False):
        return
    want: set[str] = set()
    for raw in focus_codes:
        code = extract_taxonomy_code(str(raw or "")) or str(raw or "").strip().upper()
        if code:
            want.add(code)
    if not want:
        return
    for doc in getattr(retriever, "_docs", []) or []:
        code = str(doc.get("code") or "").strip().upper()
        if code in want and code not in by_code:
            by_code[code] = barsel_item_from_retriever_hit(doc)


def _hitl_rag_k() -> int:
    try:
        return max(3, min(12, int(os.getenv("HITL_RAG_K") or "6")))
    except ValueError:
        return 6


def barsel_item_from_retriever_hit(hit: Dict[str, Any]) -> BarselTaxonomyItem:
    """Mongo retriever hit → HITL BarselTaxonomyItem."""
    code = str(hit.get("code") or "").strip().upper()
    tr = (hit.get("content") or {}).get("tr") or {}
    raw_kw = hit.get("keywords")
    keywords: List[str] = []
    if isinstance(raw_kw, list):
        for entry in raw_kw:
            keywords.extend(parse_keywords(str(entry)))
    else:
        kw_tr = (hit.get("keywords") or {}).get("tr") or []
        if isinstance(kw_tr, list):
            for entry in kw_tr:
                keywords.extend(parse_keywords(str(entry)))
    keywords = list(dict.fromkeys(k for k in keywords if k))
    probs = tr.get("typical_problems") or []
    if not isinstance(probs, list):
        probs = []
    rel = hit.get("related_codes") or []
    return BarselTaxonomyItem(
        code=code,
        title=str(tr.get("title") or code),
        definition=str(tr.get("definition") or ""),
        selection_criteria=str(tr.get("selection_criteria") or "").strip(),
        typical_problems=[str(p).strip() for p in probs if str(p).strip()],
        keywords=keywords,
        section_ids=[str(s) for s in (hit.get("section_ids") or [])],
        related_codes=[str(c).upper() for c in rel if c],
        cause_type=str(hit.get("cause_type") or ""),
    )


def merge_barsel_items(
    primary: BarselTaxonomyItem,
    secondary: BarselTaxonomyItem,
) -> BarselTaxonomyItem:
    """Mongo (primary) + statik JSON — daha zengin alanları birleştir."""
    keywords = list(dict.fromkeys(primary.keywords + secondary.keywords))
    probs = list(dict.fromkeys(primary.typical_problems + secondary.typical_problems))
    return BarselTaxonomyItem(
        code=primary.code or secondary.code,
        title=primary.title or secondary.title,
        definition=primary.definition or secondary.definition,
        selection_criteria=primary.selection_criteria or secondary.selection_criteria,
        typical_problems=probs,
        keywords=keywords,
        section_ids=primary.section_ids or secondary.section_ids,
        related_codes=primary.related_codes or secondary.related_codes,
        cause_type=primary.cause_type or secondary.cause_type,
    )


def build_hitl_taxonomy_index(
    incident_context: str,
    focus_codes: Optional[List[str]] = None,
    *,
    static_by_code: Optional[Dict[str, BarselTaxonomyItem]] = None,
    retriever: Any = None,
) -> tuple[List[BarselTaxonomyItem], Dict[str, BarselTaxonomyItem]]:
    """
    HITL taksonomi indeksi.

    Varsayılan (HITL_ALLOW_JSON_HSG_FALLBACK yok): yalnızca Mongo RAG + retriever doc lookup.
    Legacy fallback açıksa: statik JSON ile birleştirilir.
    """
    mongo_only = hitl_mongo_only_sources()
    static = {} if mongo_only else (static_by_code or {})
    by_code: Dict[str, BarselTaxonomyItem] = dict(static)

    query = (incident_context or "").strip()
    rag_active = (
        hitl_mongo_rag_enabled()
        and retriever is not None
        and getattr(retriever, "connected", False)
    )
    if rag_active and query:
        try:
            hits = retriever.retrieve(
                query[:4000],
                k=_hitl_rag_k(),
                min_score=0.02,
                keyword_pool=max(20, _hitl_rag_k() * 3),
            )
        except Exception:
            hits = []
        for hit in hits:
            item = barsel_item_from_retriever_hit(hit)
            if not item.code:
                continue
            prev = by_code.get(item.code)
            by_code[item.code] = merge_barsel_items(item, prev) if prev else item

    if rag_active:
        _supplement_codes_from_retriever_docs(by_code, focus_codes or [], retriever)
    elif not mongo_only:
        for raw in focus_codes or []:
            code = extract_taxonomy_code(str(raw or "")) or str(raw or "").strip().upper()
            if code and code not in by_code and code in static:
                by_code[code] = static[code]

        if query and len(by_code) < 3:
            pool = list(by_code.values()) or list(static.values())
            for code in infer_barsel_codes_from_text(query, pool, top_k=3):
                if code not in by_code and code in static:
                    by_code[code] = static[code]

    return list(by_code.values()), by_code


def pick_keywords_for_hitl(
    item: BarselTaxonomyItem,
    incident_text: str,
    *,
    slot_index: int = 0,
    max_keywords: int = 2,
) -> List[str]:
    """Mongo keywords.tr — olay metnine göre sırala, slot ile çeşitlendir."""
    kws = [k.strip() for k in item.keywords if len(k.strip()) >= 3]
    if not kws:
        return []
    incident = incident_text or ""

    def rank_key(kw: str) -> tuple[float, str]:
        return (keyword_overlap_score(incident, kw), kw)

    ranked = sorted(kws, key=rank_key, reverse=True)
    start = max(0, slot_index) % len(ranked)
    rotated = ranked[start:] + ranked[:start]
    return rotated[:max_keywords]


def pick_typical_problems_for_hitl(
    item: BarselTaxonomyItem,
    incident_text: str,
    why_level: int,
    *,
    max_problems: int = 1,
    min_relevance: float | None = None,
) -> List[str]:
    probs = [p for p in item.typical_problems if p.strip()]
    if not probs:
        if item.definition:
            first = re.split(r"[.!?]\s+", item.definition.strip(), maxsplit=1)[0].strip()
            if len(first) >= 20:
                probs = [first]
    if not probs:
        return []
    incident = incident_text or ""
    threshold = hitl_probe_min_relevance() if min_relevance is None else min_relevance

    def rank_key(problem: str) -> tuple[float, str]:
        score = probe_context_relevance(problem, item, incident)
        return (score, problem)

    ranked = sorted(probs, key=rank_key, reverse=True)
    filtered = [p for score, p in [(rank_key(x)[0], x) for x in ranked] if score >= threshold]
    if not filtered:
        return []
    start = (max(1, why_level) - 1) % len(filtered)
    rotated = filtered[start:] + filtered[:start]
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
