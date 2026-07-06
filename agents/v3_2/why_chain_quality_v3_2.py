"""
V3.2 — Olay/zarar merkezli 5-Why W1.

V3.1 hatası (build_event_why1_question):
  İlk uzun cümleden "Neden <montaj/faaliyet> meydana geldi?" üretir.
  Örnek hata: "Neden … segment strand halat montaj meydana geldi?"
  Doğrusu: olayın zararlı sonucu — "Neden Garcia 3,8 m yükseklikten düşerek ağır yaralandı?"

V3.2 akış:
  W1 soru — tüm dallarda ORTAK, olayın zarar/yaralanma/maruziyet merceği
  W1 cevap — dal başına A/B (BARSEL + evidence_tr)
  W2–W5 — why_chain_v3_2 (W2 A/B cevabına neden; W3–W5 → C/D)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

try:
    from agents.why_chain_quality import (
        enforce_short_why_question,
        immediate_cause_sentence,
        strip_barsel_answer_prefix,
    )
except ImportError:
    from ..why_chain_quality import (
        enforce_short_why_question,
        immediate_cause_sentence,
        strip_barsel_answer_prefix,
    )

# Faaliyet/montaj cümleleri W1 için uygun değil
_ACTIVITY_MARKERS = (
    "montaj",
    "demontaj",
    "strand halat",
    "operasyon",
    "faaliyet",
    "çalışma başlad",
    "calisma baslad",
    "meydana geldi",
    "gerçekleştir",
    "yapıldı",
    "yapilm",
)

_HARM_MARKERS = (
    "yaraland",
    "yaralan",
    "ağır yar",
    "agir yar",
    "hayati",
    "ölüm",
    "olum",
    "düş",
    "dus",
    "düşme",
    "maruz",
    "zehir",
    "çarp",
    "carp",
    "sıkış",
    "sikis",
    "kesik",
    "yanık",
    "yanik",
)

_RE_HEIGHT = re.compile(
    r"(\d+[,.]?\d*)\s*(?:metre|m)\b",
    re.IGNORECASE,
)
_RE_NAME_BEFORE_HARM = re.compile(
    r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)\b"
    r"(?:[^.!?]{0,80}?(?:yaraland|yaralan|düş|dus|maruz))",
    re.IGNORECASE,
)
_RE_KAZAZEDE = re.compile(r"\bkazazede\b", re.IGNORECASE)
_RE_GARCIA = re.compile(r"\bGarcia\b", re.IGNORECASE)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _sentences(text: str) -> List[str]:
    raw = _normalize(text)
    if not raw:
        return []
    parts = re.split(r"(?<=[.!?])\s+", raw)
    return [p.strip() for p in parts if len(p.strip()) >= 12]


def _harm_score(sentence: str) -> int:
    low = sentence.lower()
    score = sum(3 for m in _HARM_MARKERS if m in low)
    score -= sum(4 for m in _ACTIVITY_MARKERS if m in low)
    if _RE_HEIGHT.search(sentence) and any(k in low for k in ("düş", "dus", "yüksek")):
        score += 5
    if _RE_GARCIA.search(sentence) or _RE_KAZAZEDE.search(sentence):
        score += 2
    return score


def _pick_harm_sentence(incident_text: str) -> str:
    sents = _sentences(incident_text)
    if not sents:
        return _normalize(incident_text)[:200]
    ranked = sorted(sents, key=_harm_score, reverse=True)
    best = ranked[0]
    if _harm_score(best) <= 0:
        # Zarar cümlesi yoksa tüm metinde en yüksek skorlu parça
        for s in ranked:
            if _harm_score(s) > 0:
                return s
        return sents[-1] if len(sents) > 1 else sents[0]
    return best


def _extract_subject(incident_text: str, harm_sentence: str) -> str:
    if _RE_GARCIA.search(incident_text) or _RE_GARCIA.search(harm_sentence):
        return "Garcia"
    m = _RE_NAME_BEFORE_HARM.search(harm_sentence)
    if m:
        name = m.group(1).strip()
        if name.lower() not in ("batı", "bati", "doğu", "dogu", "vsl", "eak"):
            return name
    low = incident_text.lower()
    if "operatör" in low:
        return "operatör"
    if "kazazede" in low:
        return "kazazede"
    if "personel" in low:
        return "personel"
    if "çalışan" in low or "calisan" in low:
        return "çalışan"
    return "personel"


def build_incident_harm_why1_question_heuristic(
    incident_text: str,
    immediate_cause: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Olayın zararlı sonucundan W1 sorusu — faaliyet/montaj cümlesi kullanılmaz.
    """
    text = _normalize(incident_text)
    harm = _pick_harm_sentence(text)
    low_harm = harm.lower()
    subject = _extract_subject(text, harm)

    height_m = _RE_HEIGHT.search(harm) or _RE_HEIGHT.search(text)
    height = height_m.group(1).replace(",", ".") if height_m else ""

    if any(k in low_harm for k in ("düş", "dus", "yüksekten", "yuksekten")) or (
        height and any(k in text.lower() for k in ("düş", "dus", "yaraland"))
    ):
        if height:
            return enforce_short_why_question(
                f"Neden {subject} {height} metre yükseklikten düşerek ağır yaralandı?"
            )
        return enforce_short_why_question(
            f"Neden {subject} yükseklikten düşerek ağır yaralandı?"
        )

    if any(k in low_harm for k in ("maruz", "solvent", "buhar", "kimyasal")):
        if "solvent" in text.lower() or "buhar" in text.lower():
            return enforce_short_why_question(
                f"Neden {subject} solvent buharına maruz kaldı?"
            )
        return enforce_short_why_question(
            f"Neden {subject} kimyasal maruziyete uğradı?"
        )

    if any(k in low_harm for k in ("çarp", "carp", "carpm")):
        return enforce_short_why_question(
            f"Neden {subject} çarpma sonucu yaralandı?"
        )

    # Genel zarar cümlesi — faaliyet eklerini soy
    clause = re.sub(
        r"\s*(meydana\s+gel\w*|gerçekleş\w*|yaşan\w*|oluş\w*|olmuştur|oldu)[.!?]?\s*$",
        "",
        harm,
        flags=re.IGNORECASE,
    ).strip().rstrip(".!?,;:")
    clause = re.sub(
        r"^(?:\d{1,2}[./]\d{1,2}[./]\d{2,4}\s*(?:tarihinde)?\s*)",
        "",
        clause,
        flags=re.IGNORECASE,
    ).strip()
    words = clause.split()
    if len(words) > 12:
        clause = " ".join(words[:12])
    if not clause:
        return "Neden bu olayda personel yaralandı?"
    return enforce_short_why_question(f"Neden {subject} {clause}?")


def build_trainset_why1_question_heuristic(
    incident_text: str,
    immediate_cause: Optional[Dict[str, Any]] = None,
) -> str:
    """Geriye dönük alias — harm-centric W1."""
    return build_incident_harm_why1_question_heuristic(incident_text, immediate_cause)


def build_trainset_why1_question(
    incident_text: str,
    immediate_cause: Optional[Dict[str, Any]] = None,
    *,
    dspy_predict: Any = None,
) -> str:
    """DSPy ile olay-zarar W1; başarısızsa heuristic."""
    incident = str(incident_text or "")[:3500]
    if dspy_predict is not None:
        try:
            result = dspy_predict(incident_summary=incident)
            q = enforce_short_why_question(str(getattr(result, "question", "") or "").strip())
            low_q = q.lower()
            if q.lower().startswith("neden") and "?" in q:
                # Faaliyet sorusu reddi
                if not any(m in low_q for m in _ACTIVITY_MARKERS):
                    return q
        except Exception:  # noqa: BLE001
            pass
    return build_incident_harm_why1_question_heuristic(incident, immediate_cause)


def immediate_cause_ab_answer(
    immediate: Dict[str, Any],
    *,
    retriever: Any = None,
) -> Tuple[str, str]:
    """
    NEDEN 1 cevabı: A/B bandı — BARSEL Mongo + immediate_cause.

    Öncelik: evidence_tr (mekanizma) → cause_tr → resmi başlık.
    """
    imm = immediate if isinstance(immediate, dict) else {}
    code = str(imm.get("code") or "").strip().upper()

    try:
        from agents.barsel_taxonomy import (
            official_title_tr_for_code,
            taxonomy_item_for_code,
        )
    except ImportError:
        from ..barsel_taxonomy import (
            official_title_tr_for_code,
            taxonomy_item_for_code,
        )

    item = taxonomy_item_for_code(code, retriever=retriever) if code else None
    official = (
        (item.title if item else "")
        or official_title_tr_for_code(code)
        or str(imm.get("standard_title_tr") or "").strip()
    )
    evidence = strip_barsel_answer_prefix(str(imm.get("evidence_tr") or "").strip())
    cause_tr = strip_barsel_answer_prefix(str(imm.get("cause_tr") or official or "").strip())

    if evidence and len(evidence) >= 25:
        body = evidence
    elif cause_tr:
        body = cause_tr
    else:
        body = official

    return immediate_cause_sentence(body), code
