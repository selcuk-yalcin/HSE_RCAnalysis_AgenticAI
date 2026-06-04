"""
BARSEL tabanlı HITL disambiguation + taxonomy_gap + why-probe code-specific soru bankası.

Kullanıcıya kod göstermez; typical_problems, selection_criteria ve contrast
soruları BARSEL JSON'dan gelir. Yetersiz kalırsa band-prefix fallback (soru
metni only — HSG yönler/kod ipuçları yok).
"""
from __future__ import annotations

import re
from typing import Any

from agents.barsel_taxonomy import (
    BarselTaxonomyItem,
    extract_taxonomy_code,
    find_contrast_code,
    hitl_allow_legacy_fallback,
    hitl_mongo_only_sources,
    load_barsel_taxonomy_items,
    pick_keywords_for_hitl,
    pick_typical_problems_for_hitl,
    split_selection_criteria,
)

_KEYWORD_QUESTION_TEMPLATES = (
    "Bu olayda «{kw}» ifadesi gerçekten geçerli miydi?",
    "Tanık veya kayıtlarda «{kw}» ile örtüşen bir durum var mıydı?",
    "«{kw}» bu olayı açıklamak için doğru bir çerçeve mi?",
)
from agents.hitl_disambiguation_bank import GENEL_DISAMBIGUATION, HSG245_DISAMBIGUATION

# Eksik kategori soruları — QuestionEngine metinleri, HSG kod bağlantısı yok
BARSEL_TAXONOMY_GAP_TEMPLATES: dict[str, dict[str, Any]] = {
    "kronoloji": {
        "description": "Olayın zamansal akışı",
        "questions": [
            {
                "question": "Olay hangi tarih ve saatte meydana geldi?",
                "required": True,
            },
            {
                "question": "Olay öncesi son 2 saat içinde ne tür aktiviteler yapılıyordu?",
                "required": False,
            },
        ],
    },
    "prosedür": {
        "description": "İş talimatları ve prosedürler",
        "questions": [
            {
                "question": "Bu iş için yazılı bir prosedür/iş talimatı var mıydı?",
                "required": True,
            },
            {
                "question": "Prosedür sahada uygulanabilir miydi, yoksa kağıt üzerinde mi kaldı?",
                "required": True,
            },
        ],
    },
    "tanık": {
        "description": "Görgü tanıkları ve gözlemler",
        "questions": [
            {
                "question": "Olay sırasında başka kimler alanda bulunuyordu?",
                "required": True,
            },
            {
                "question": "Görgü tanıkları olayı nasıl anlattı?",
                "required": False,
            },
        ],
    },
    "yönetim": {
        "description": "Yönetim ve organizasyonel faktörler",
        "questions": [
            {
                "question": "Üretim veya teslim baskısı güvenlik uygulamalarını etkiledi mi?",
                "required": True,
            },
            {
                "question": "Yönetim bu riski veya sapmayı daha önce biliyor muydu?",
                "required": False,
            },
        ],
    },
    "ekipman": {
        "description": "Ekipman ve bakım",
        "questions": [
            {
                "question": "Olayda kullanılan ekipman/alet hangisiydi ve çalışır durumda mıydı?",
                "required": True,
            },
            {
                "question": "Ekipmanın son bakım veya kontrol tarihi nedir?",
                "required": False,
            },
        ],
    },
    "eğitim": {
        "description": "Eğitim ve yeterlilik",
        "questions": [
            {
                "question": "Personel bu iş için eğitim almış mıydı?",
                "required": True,
            },
            {
                "question": "Eğitim pratik uygulamayı kapsıyor muydu?",
                "required": False,
            },
        ],
    },
    "ppe": {
        "description": "Kişisel koruyucu donanım",
        "questions": [
            {
                "question": "Gerekli koruyucu ekipman (KKD) kullanıldı mı?",
                "required": True,
            },
            {
                "question": "KKD sahada mevcut ve erişilebilir miydi?",
                "required": False,
            },
        ],
    },
}

# Why-probe code-specific: band düzeyinde ek derinlik (kod yok)
BARSEL_BAND_CODE_SPECIFIC: dict[str, list[str]] = {
    "A": [
        "Bu davranış daha önce de görülmüş müydü?",
        "Çalışan kuralı bilerek mi ihlal etti, yoksa farkında mı değildi?",
    ],
    "B": [
        "Bu koşul olay öncesinden beri mi vardı, yoksa anlık mı oluştu?",
        "Benzer koşullar daha önce de rapor edilmiş miydi?",
    ],
    "C": [
        "Çalışanın bu işte yeterli deneyimi ve yeterliliği vardı mı?",
        "Yorgunluk, stres veya sağlık durumu bu olayı etkilemiş olabilir mi?",
    ],
    "D": [
        "Bu eksiklik için daha önce aksiyon planlanmış mıydı?",
        "Sorumluluk ve takip mekanizması net miydi?",
    ],
}


def _band_code_specific_probes(code: str, why_level: int) -> list[str]:
    band = (code or "").strip().upper()[:1]
    templates = BARSEL_BAND_CODE_SPECIFIC.get(band) or []
    if not templates:
        return []
    start = (max(1, why_level) - 1) % len(templates)
    rotated = templates[start:] + templates[:start]
    return rotated[:1]


def _code_specific_probes_for_item(
    item: BarselTaxonomyItem,
    all_items: list[BarselTaxonomyItem],
    incident_context: str,
    why_level: int,
) -> list[dict[str, Any]]:
    """Deep taxonomy sorularından farklı tamamlayıcı why-probe'lar."""
    out: list[dict[str, Any]] = []

    clauses = split_selection_criteria(item.selection_criteria, max_clauses=3)
    if len(clauses) > 1:
        start = (max(1, why_level) - 1) % len(clauses)
        rotated = clauses[start:] + clauses[:start]
        for clause in rotated[1:2]:
            out.append(
                {
                    "question": f"«{item.title}» için şu ayırıcı koşul geçerli miydi: {clause}?",
                    "code": item.code,
                    "code_description": item.title,
                    "hsg245": item.title,
                    "yönler": {"probe_type": "selection_criteria"},
                    "barsel": True,
                }
            )

    kws = [k for k in item.keywords if len(k.strip()) >= 4][:3]
    if kws:
        kw_label = ", ".join(f"«{k}»" for k in kws[:2])
        out.append(
            {
                "question": f"Olay anlatımında {kw_label} ile ilgili ifadeler var mıydı?",
                "code": item.code,
                "code_description": item.title,
                "hsg245": item.title,
                "yönler": {"probe_type": "keywords"},
                "barsel": True,
            }
        )

    if item.related_codes:
        rel_code = item.related_codes[0].upper()
        rel_item = next((o for o in all_items if o.code == rel_code), None)
        if rel_item and rel_item.code != item.code:
            out.append(
                {
                    "question": (
                        f"Bu olay «{item.title}» mi yoksa «{rel_item.title}» ile mi "
                        f"daha iyi açıklanır?"
                    ),
                    "code": item.code,
                    "code_description": item.title,
                    "hsg245": item.title,
                    "yönler": {"probe_type": "related_code", "related_code": rel_code},
                    "barsel": True,
                }
            )

    if why_level >= 2 and item.definition:
        snippet = re.split(r"[.!?]\s+", item.definition.strip(), maxsplit=1)[0].strip()
        if len(snippet) >= 40:
            short = snippet if len(snippet) <= 140 else snippet[:137].rstrip() + "…"
            out.append(
                {
                    "question": f"Bu tanım olayı yansıtıyor mu: {short}?",
                    "code": item.code,
                    "code_description": item.title,
                    "hsg245": item.title,
                    "yönler": {"probe_type": "definition"},
                    "barsel": True,
                }
            )

    for probe in _band_code_specific_probes(item.code, why_level):
        out.append(
            {
                "question": probe,
                "code": item.code,
                "code_description": item.title,
                "hsg245": item.title,
                "yönler": {"probe_type": "band_followup"},
                "barsel": True,
            }
        )

    probs = pick_typical_problems_for_hitl(
        item,
        incident_context,
        why_level=max(1, why_level + 1),
        max_problems=1,
    )
    for prob in probs:
        out.append(
            {
                "question": f"«{item.title}» bağlamında şu durum geçerli miydi: {prob}?",
                "code": item.code,
                "code_description": item.title,
                "hsg245": item.title,
                "yönler": {"probe_type": "typical_problem_rotated"},
                "barsel": True,
            }
        )

    return out


def get_barsel_code_specific_questions(
    suspected_codes: list[str],
    *,
    why_level: int = 1,
    incident_context: str = "",
    max_per_code: int = 3,
    max_total: int = 6,
    barsel_items: list[BarselTaxonomyItem] | None = None,
    barsel_by_code: dict[str, BarselTaxonomyItem] | None = None,
) -> list[dict[str, Any]]:
    if barsel_by_code is not None:
        by_code = {k.upper(): v for k, v in barsel_by_code.items() if v.code}
        items = barsel_items if barsel_items is not None else list(by_code.values())
    else:
        items = load_barsel_taxonomy_items()
        if not items:
            return []
        by_code = {i.code.upper(): i for i in items if i.code}

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in suspected_codes:
        code = extract_taxonomy_code(str(raw or "")) or str(raw or "").strip().upper()
        item = by_code.get(code)
        if not item:
            continue
        for row in _code_specific_probes_for_item(
            item, items, incident_context, why_level=why_level
        ):
            q = str(row.get("question") or "").strip()
            if not q or q in seen:
                continue
            seen.add(q)
            out.append(row)
            if sum(1 for r in out if r.get("code") == code) >= max_per_code:
                break
        if len(out) >= max_total:
            break
    return out[:max_total]


def _band_fallback_questions(code: str) -> list[dict[str, Any]]:
    """HSG bankasından yalnızca soru metni; kod/yön ipuçları kullanıcıya gitmez."""
    code = (code or "").strip().upper()
    if code in HSG245_DISAMBIGUATION:
        templates = HSG245_DISAMBIGUATION[code]
    else:
        prefix = code[:2] if len(code) >= 2 else ""
        templates = None
        for key in HSG245_DISAMBIGUATION:
            if key.startswith(prefix):
                templates = HSG245_DISAMBIGUATION[key]
                break
        if not templates:
            templates = GENEL_DISAMBIGUATION
    return [{"soru": t["soru"], "hsg245": "", "yönler": {}} for t in templates]


def _questions_from_barsel_item(
    item: BarselTaxonomyItem,
    all_items: list[BarselTaxonomyItem],
    incident_context: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for prob in pick_typical_problems_for_hitl(
        item, incident_context, why_level=1, max_problems=2
    ):
        out.append(
            {
                "soru": f"Bu olayda şu durum geçerli miydi: {prob}?",
                "hsg245": item.title,
                "yönler": {"probe_type": "typical_problem"},
            }
        )
    for clause in split_selection_criteria(item.selection_criteria, max_clauses=1):
        out.append(
            {
                "soru": f"Bu olayda şu koşul ne ölçüde geçerliydi: {clause}?",
                "hsg245": item.title,
                "yönler": {"probe_type": "selection_criteria"},
            }
        )
    slot = len(out)
    for kw in pick_keywords_for_hitl(
        item, incident_context, slot_index=slot, max_keywords=2
    ):
        tpl = _KEYWORD_QUESTION_TEMPLATES[slot % len(_KEYWORD_QUESTION_TEMPLATES)]
        out.append(
            {
                "soru": tpl.format(kw=kw),
                "hsg245": item.title,
                "yönler": {"probe_type": "keyword_rag", "keyword": kw},
            }
        )
        slot += 1

    contrast = find_contrast_code(item, all_items)
    if contrast:
        out.append(
            {
                "soru": (
                    f"Bu olay «{item.title}» kapsamında mı, yoksa "
                    f"«{contrast.title}» kapsamında mı değerlendirilmeli? "
                    f"Ayırmamıza yardımcı somut kanıt var mı?"
                ),
                "hsg245": item.title,
                "yönler": {"probe_type": "contrast", "contrast_code": contrast.code},
            }
        )
    return out


def get_barsel_disambiguation_questions(
    cause_code: str,
    *,
    items: list[BarselTaxonomyItem] | None = None,
    by_code: dict[str, BarselTaxonomyItem] | None = None,
    incident_context: str = "",
) -> list[dict[str, Any]]:
    code = extract_taxonomy_code(cause_code) or (cause_code or "").strip().upper()
    legacy = hitl_allow_legacy_fallback()
    if items is None and by_code is None:
        if hitl_mongo_only_sources():
            return []
        items = load_barsel_taxonomy_items()
    if by_code is None:
        by_code = {i.code.upper(): i for i in (items or []) if i.code}
    pool_items = items if items is not None else list(by_code.values())

    item = by_code.get(code)
    if item:
        qs = _questions_from_barsel_item(item, pool_items, incident_context)
        if len(qs) >= 2 or not legacy:
            return qs
        seen = {q["soru"] for q in qs}
        for fb in _band_fallback_questions(code):
            if fb["soru"] not in seen:
                qs.append(fb)
                seen.add(fb["soru"])
            if len(qs) >= 5:
                break
        return qs
    if legacy:
        return _band_fallback_questions(code)
    return []


def build_barsel_questions_for_causes(
    immediate_causes: list[dict],
    incident_context: str = "",
    *,
    barsel_items: list[BarselTaxonomyItem] | None = None,
    barsel_by_code: dict[str, BarselTaxonomyItem] | None = None,
) -> list[dict[str, Any]]:
    if barsel_by_code is not None:
        by_code = {k.upper(): v for k, v in barsel_by_code.items() if v.code}
        items = barsel_items if barsel_items is not None else list(by_code.values())
    elif hitl_mongo_only_sources():
        return []
    else:
        items = load_barsel_taxonomy_items()
        if not items:
            return []
        by_code = {i.code.upper(): i for i in items if i.code}
    questions: list[dict[str, Any]] = []
    seen: set[str] = set()

    for cause in immediate_causes[:3]:
        raw_code = str(cause.get("code") or "").strip()
        code = extract_taxonomy_code(raw_code) or raw_code.upper()
        item = by_code.get(code)
        cause_desc = (
            cause.get("cause_tr")
            or cause.get("standard_title_tr")
            or (item.title if item else code)
        )
        for q in get_barsel_disambiguation_questions(
            code,
            items=items,
            by_code=by_code,
            incident_context=incident_context,
        )[:3]:
            soru = q["soru"]
            if soru in seen:
                continue
            seen.add(soru)
            questions.append(
                {
                    "code": code,
                    "cause_desc": cause_desc,
                    "soru": soru,
                    "hsg245": q.get("hsg245", ""),
                    "yönler": q.get("yönler") or {},
                    "barsel": True,
                }
            )
    return questions[:8]


def _infer_incident_type(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ("elektrik", "loto", "enerji", "volt", "panel")):
        return "elektrik"
    if any(x in t for x in ("düş", "yüksek", "iskele", "korkuluk", "kemer", "platform")):
        return "düşme"
    if any(x in t for x in ("forklift", "araç", "kamyon", "istif")):
        return "forklift"
    return "generic"


def build_barsel_taxonomy_gap_questions(
    full_text: str,
    max_categories: int = 4,
    per_cat: int = 2,
) -> list[dict[str, Any]]:
    from hitl_test.hybrid_input_processor import HybridInputProcessor

    _, det = HybridInputProcessor().detect_input_level(full_text or "")
    missing = det.get("missing") or []
    if not missing:
        return []

    incident_type = _infer_incident_type(full_text)
    hip = HybridInputProcessor()
    typed_rows = {
        str(r.get("category") or ""): r
        for r in hip.generate_missing_questions(missing[:max_categories], incident_type)
    }

    out: list[dict[str, Any]] = []
    for cat in missing[:max_categories]:
        tpl = BARSEL_TAXONOMY_GAP_TEMPLATES.get(cat) or {}
        desc = tpl.get("description") or cat
        rows = list(tpl.get("questions") or [])
        typed = typed_rows.get(cat)
        if typed and typed.get("question"):
            rows = [{"question": typed["question"], "required": True}] + rows

        for i, row in enumerate(rows[:per_cat]):
            qtext = str(row.get("question") or "").strip()
            if not qtext:
                continue
            out.append(
                {
                    "source": "taxonomy_gap_barsel",
                    "code": "",
                    "cause_desc": desc,
                    "hsg245": "",
                    "soru": qtext,
                    "yönler": {},
                    "category": cat,
                    "required": bool(row.get("required")),
                    "barsel": True,
                }
            )
    return out
