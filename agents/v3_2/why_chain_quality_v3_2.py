"""
V3.2 — Trainset tarzı 5-Why W1: olaydan soru, cevap A/B (BARSEL / immediate_cause).

Referans: agents/synetic_data_preperation/hse_dspy_trainset.json (good_tr_kimya_sizinti).
V3.1'den fark: W1 sorusu "Neden … meydana geldi?" değil; olayın birincil zararlı
sonucu/maruziyeti ("Neden operatör solvent buharına maruz kaldı?").
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

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


def build_trainset_why1_question_heuristic(
    incident_text: str,
    immediate_cause: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Olay metninden trainset tarzı kısa NEDEN 1 sorusu (LLM yok).
    """
    text = re.sub(r"\s+", " ", str(incident_text or "").strip())
    low = text.lower()
    imm = immediate_cause if isinstance(immediate_cause, dict) else {}
    cause_hint = str(imm.get("cause_tr") or imm.get("standard_title_tr") or "").lower()

    subject = "operatör"
    if "operatör" not in low:
        if "personel" in low:
            subject = "personel"
        elif "çalışan" in low or "isci" in low.replace("i", "ı"):
            subject = "çalışan"
        elif "tekniker" in low:
            subject = "tekniker"
        else:
            subject = "personel"

    if any(k in low for k in ("solvent", "buhar", "kimyasal", "maruz")) or "kimya" in cause_hint:
        if "solvent" in low or "buhar" in low:
            return f"Neden {subject} solvent buharına maruz kaldı?"
        return f"Neden {subject} kimyasal maruziyete uğradı?"

    if any(k in low for k in ("düştü", "düşme", "yüksekten", "dusme", "yuksekten")):
        return f"Neden {subject} düşme riskiyle karşılaştı?"

    if any(k in low for k in ("çarp", "carp", "carpm", "çarpma")):
        return f"Neden {subject} çarpma riskiyle karşılaştı?"

    if any(k in low for k in ("sızınt", "sizint", "kaçak", "daml")):
        return "Neden proses hattında sızıntı meydana geldi?"

    if any(k in low for k in ("yangın", "yangin", "alev", "duman")):
        return "Neden yangın/duman olayı meydana geldi?"

    if any(k in low for k in ("elektrik", "akım", "akim", "çarpıl", "carpil")):
        return f"Neden {subject} elektrik riskiyle karşılaştı?"

    # İlk anlamlı cümleden kısa soru
    sentence = ""
    for line in text.splitlines():
        ln = line.strip()
        if not ln or ln.startswith("["):
            continue
        candidate = re.split(r"(?<=[.!?])\s+", ln)[0].strip()
        if len(candidate) >= 15:
            sentence = candidate
            break
        if not sentence:
            sentence = candidate
    sentence = re.sub(
        r"\s*(meydana\s+gel\w*|gerçekleş\w*|yaşan\w*|oluş\w*|olmuştur|oldu|tespit\s+edildi)[.!?]?\s*$",
        "",
        sentence,
        flags=re.IGNORECASE,
    ).strip().rstrip(".!?,;:")
    if not sentence:
        return "Neden bu olay meydana geldi?"
    words = sentence.split()
    if len(words) > 14:
        sentence = " ".join(words[:14])
    return enforce_short_why_question(f"Neden {sentence}?")


def build_trainset_why1_question(
    incident_text: str,
    immediate_cause: Optional[Dict[str, Any]] = None,
    *,
    dspy_predict: Any = None,
) -> str:
    """DSPy ile olaydan W1 sorusu; başarısızsa heuristic."""
    incident = str(incident_text or "")[:3500]
    if dspy_predict is not None:
        try:
            result = dspy_predict(incident_summary=incident)
            q = enforce_short_why_question(str(getattr(result, "question", "") or "").strip())
            if q.lower().startswith("neden") and "?" in q:
                return q
        except Exception:  # noqa: BLE001
            pass
    return build_trainset_why1_question_heuristic(incident, immediate_cause)


def immediate_cause_ab_answer(
    immediate: Dict[str, Any],
    *,
    retriever: Any = None,
) -> tuple[str, str]:
    """
    NEDEN 1 cevabı: A/B bandı — BARSEL Mongo + immediate_cause satırı.

    Öncelik: evidence_tr (mekanizma anlatımı) → resmi başlık → cause_tr.
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
