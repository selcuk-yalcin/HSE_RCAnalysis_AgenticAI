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
        demote_solution_to_cause,
        enforce_short_why_question,
        immediate_cause_sentence,
        strip_barsel_answer_prefix,
    )
except ImportError:
    from ..why_chain_quality import (
        demote_solution_to_cause,
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
# "işçisi Hasan Yıldız (32)" / "operatör Ahmet Demir"
_RE_NAMED_WORKER = re.compile(
    r"(?:işçisi|iscisi|operatör|operator|personel|çalışan|calisan|tekniker)\s+"
    r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)"
    r"(?:\s*\(\d+\))?",
    re.IGNORECASE,
)
# V3.1 hatalı W1 imzası — rapor/RCA reddi
_RE_V31_BAD_WHY1 = re.compile(r"meydana\s+gel\w*\s*\?\s*$", re.IGNORECASE)


def is_invalid_why1_question(question: str) -> bool:
    """V3.1 'meydana geldi?' veya faaliyet-paragrafı W1."""
    q = _normalize(question)
    if not q:
        return True
    low = q.lower()
    if not low.startswith("neden"):
        return True
    if _RE_V31_BAD_WHY1.search(q):
        return True
    if any(m in low for m in ("meydana geldi", "gerçekleşti", "gercelesti")):
        return True
    # Olay paragrafının aynen kopyası: çok uzun + montaj/iskele faaliyeti
    if len(q.split()) > 22 and any(m in low for m in ("montaj", "iskele", "faaliyet")):
        return True
    return False


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
    for blob in (harm_sentence, incident_text):
        m = _RE_NAMED_WORKER.search(blob)
        if m:
            return m.group(1).strip()
    m = _RE_NAME_BEFORE_HARM.search(harm_sentence)
    if m:
        name = m.group(1).strip()
        if name.lower() not in ("batı", "bati", "doğu", "dogu", "vsl", "eak", "iskele", "montaj"):
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
                if not any(m in low_q for m in _ACTIVITY_MARKERS) and not is_invalid_why1_question(q):
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
    body = _pick_why1_ab_body(imm, evidence, cause_tr, official)
    return immediate_cause_sentence(body), code


# ── V3.2 zincir kalitesi (global — tüm raporlar) ─────────────────────────────

_ORG_W1_MARKERS = (
    "prosedür",
    "değerlendirme",
    "değerlendirmesinde",
    "ita",
    "iş tehlike",
    "risk senaryosu",
    "rehberlik eksikliği",
    "yapım metot",
    "tanımlanmamıştır",
    "belirlenmiştir",
    "mevcut olmasına rağmen",
    "incelemesinde",
    "doküman",
    "form eksik",
)

_AB_MECHANISM_MARKERS = (
    "bağla",
    "takm",
    "kullan",
    "düş",
    "açıld",
    "mandall",
    "kanca",
    "kemeri",
    "kemersiz",
    "gösteril",
    "doğrula",
    "uyarı",
    "devam et",
    "servis dışı",
    "deform",
    "maruz",
    "çarp",
    "sıkış",
)

_FOCUS_PROMPTS: Dict[str, str] = {
    "equipment_maintenance": (
        "DAL ODAĞI — Bakım / varlık bütünlüğü / ekipman güvenilirliği: "
        "deformasyon, servis dışı bırakma, muayene, periyodik kontrol, VSL/HANDAR sorumluluk. "
        "Süpervizör, TRIC veya yetkinlik konularına kayma."
    ),
    "supervision_leadership": (
        "DAL ODAĞI — Liderlik / gözetim / güvenlik kültürü: "
        "süpervizör hold point, sözlü uyarı yerine fiziksel doğrulama, ankraj gösterme, "
        "ince ayar fazı gözetimi. Genel iş izni/PTW veya ekipman muayenesine kayma."
    ),
    "competence_workforce": (
        "DAL ODAĞI — Eğitim / yetkinlik / işgücü: "
        "işe dönüş, TRIC katılımı, görev değişikliği, sınırlı deneyim, atama onayı. "
        "Mandal/kanca deformasyonu veya genel denetim sistemine kayma."
    ),
    "culture_behavior": (
        "DAL ODAĞI — Davranışsal normalizasyon / güvenlik kültürü: "
        "güvensiz pratiklerin normalleşmesi, yaptırımsız tekrar, üst gözetim döngüsü, "
        "iç denetim. Yetkinlik/eğitim veya ekipman muayenesine kayma."
    ),
}

_TOPIC_FORBIDDEN: Dict[str, Tuple[str, ...]] = {
    "supervision_leadership": (
        "mandal deformasyon",
        "periyodik kontrol kaydı",
        "zincir donanım",
        "tric bilgilendirme",
        "işe dönüş",
    ),
    "competence_workforce": (
        "mandal deformasyon",
        "kanca emniyet mandal",
        "periyodik kontrol kaydı",
        "zincir donanım",
    ),
    "culture_behavior": (
        "tric",
        "yetkinlik değerlendirme",
        "kol kırığı",
        "işe dönüş",
        "mandal deformasyon",
    ),
    "equipment_maintenance": (
        "tric",
        "işe dönüş",
        "davranışsal şartlan",
    ),
}


def _pick_why1_ab_body(
    imm: Dict[str, Any],
    evidence: str,
    cause_tr: str,
    official: str,
) -> str:
    """W1 cevabı A/B mekanizma; belge/İTA boşluğu değil."""
    candidates = [evidence, cause_tr, official]
    for cand in candidates:
        c = str(cand or "").strip()
        if c and not is_invalid_why1_ab_answer(c):
            return c
    return str(evidence or cause_tr or official or "").strip()


def is_invalid_why1_ab_answer(answer: str) -> bool:
    """W1 cevabı organizasyonel belge boşluğu mu (A/B mekanizma değil)?"""
    low = _normalize(answer).lower()
    if not low:
        return True
    has_org = any(m in low for m in _ORG_W1_MARKERS)
    has_mech = any(m in low for m in _AB_MECHANISM_MARKERS)
    if has_org and not has_mech:
        return True
    if low.startswith("iş tehlike") or "yapım metotları inceleme" in low:
        return True
    return False


def resolve_branch_focus(
    immediate_cause: Dict[str, Any],
    branch_index: int = 1,
) -> Tuple[str, str]:
    """Kritik faktör teması → dal odağı (KF başlığıyla uyumlu derinleşme)."""
    code = str(immediate_cause.get("code") or "").strip().upper()
    cause = str(immediate_cause.get("cause_tr") or "").lower()
    evidence = str(immediate_cause.get("evidence_tr") or "").lower()
    title = str(immediate_cause.get("standard_title_tr") or "").lower()
    blob = f"{cause} {evidence} {title}"

    if any(k in blob for k in ("şartlan", "normalleş", "davranışsal norm", "kültür")):
        return "culture_behavior", _FOCUS_PROMPTS["culture_behavior"]

    if any(k in blob for k in (
        "yetkinlik", "eğitim", "tric", "işe dönüş", "deneyim", "görev değiş",
        "beceri", "yeterlilik", "işgücü", "atama",
    )):
        return "competence_workforce", _FOCUS_PROMPTS["competence_workforce"]

    if any(k in blob for k in (
        "süpervizör", "gözetim", "liderlik", "hold point", "doğrulama",
        "sözlü uyarı", "ankraj nokta",
    )):
        return "supervision_leadership", _FOCUS_PROMPTS["supervision_leadership"]

    if code.startswith("B") or any(k in blob for k in (
        "kanca", "mandal", "deform", "ekipman", "bakım", "muayene",
        "kaldırma ekipman", "zincir", "vinç", "servis dışı",
    )):
        return "equipment_maintenance", _FOCUS_PROMPTS["equipment_maintenance"]

    keys = (
        "equipment_maintenance",
        "supervision_leadership",
        "competence_workforce",
        "culture_behavior",
    )
    key = keys[(max(1, branch_index) - 1) % len(keys)]
    return key, _FOCUS_PROMPTS[key]


def topic_drift_violation(text: str, branch_focus: str, *, level: int = 3) -> Optional[str]:
    """Dal odağı dışı konuya kayma (ör. KF3'te mandal)."""
    if level < 3 or not branch_focus:
        return None
    low = _normalize(text).lower()
    for phrase in _TOPIC_FORBIDDEN.get(branch_focus, ()):
        if phrase in low:
            return f"dal odağı dışı konu: {phrase}"
    if branch_focus == "supervision_leadership" and level >= 3:
        if "iş izni" in low or "ptw" in low:
            if not any(k in low for k in ("süpervizör", "gözetim", "hold point", "doğrula")):
                return "iş izni/PTW'ye kayma (gözetim odağı kayboldu)"
    return None


def repair_why_question(question: str) -> str:
    """Beyan cümlesini 'Neden …?' soru formuna çevir."""
    q = _normalize(question)
    if not q:
        return "Neden bu durum oluştu?"
    if not q.endswith("?"):
        q = q.rstrip(".!") + "?"
    low = q.lower()
    q = re.sub(r"\s+var\s+mıydı\?\s*$", " yoktu?", q, flags=re.IGNORECASE)
    q = re.sub(r"\s+var\s+mı\?\s*$", " yok muydu?", q, flags=re.IGNORECASE)
    if not low.startswith("neden"):
        body = q.rstrip("?").strip()
        if re.match(r"^(kim|hangi)\b", body, re.IGNORECASE):
            body = re.sub(r"^(kim|hangi)\s+", "", body, flags=re.IGNORECASE)
            q = f"Neden {body}?"
        elif re.match(r"^[A-ZÇĞİÖŞÜ]", body):
            q = f"Neden {body[0].lower()}{body[1:]}?"
            if not q.endswith("?"):
                q += "?"
    q = re.sub(r"\bnedeninin\s+nedeni\s+nedir\?\s*$", "?", q, flags=re.IGNORECASE)
    return enforce_short_why_question(q)


def is_valid_why_question(
    question: str,
    prev_answer: str = "",
    *,
    level: int = 2,
) -> bool:
    """Geçerli nedensellik sorusu mu (beyan / kopuk zincir değil)."""
    q = repair_why_question(question)
    low = q.lower()
    if not q.endswith("?"):
        return False
    if not low.startswith("neden "):
        return False
    if "var mıydı" in low or "var midı" in low:
        return False
    if re.search(r"tarafından\s+tanımlanmamıştır\?\s*$", low) and "neden" not in low[:12]:
        return False
    if level >= 2 and prev_answer:
        try:
            from agents.why_chain_quality import validate_causal_link as _vcl
        except ImportError:
            from ..why_chain_quality import validate_causal_link as _vcl
        if not _vcl(prev_answer, q, min_shared=1):
            return False
    return True


def build_why2_from_ab_answer(ab_answer: str, branch_focus: str = "") -> str:
    """
    W2: W1 A/B cevabının alt nedeni — 'Neden emniyet kemeri oluştu?' hatasını önler.
    """
    text = demote_solution_to_cause(_normalize(ab_answer))
    if not text:
        return "Neden bu doğrudan neden meydana geldi?"

    low = text.lower()
    # Dal-özel kısa kalıplar
    if "emniyet kemeri" in low or "emniyet kemer" in low:
        if any(k in low for k in ("ankraj", "yüke", "yük alt", "sabitsiz")):
            return enforce_short_why_question(
                "Neden emniyet kemeri sabit ankraj yerine yüklü veya sabitsiz noktaya bağlandı?"
            )
        if "süpervizör" in low or "uyarı" in low:
            return enforce_short_why_question(
                "Neden süpervizör ankraj noktasını göstermeden sözlü uyarıyla yetindi?"
            )
    if any(k in low for k in ("deform", "mandal", "kanca")) and any(
        k in low for k in ("servis", "kullan", "devam", "bırak")
    ):
        return enforce_short_why_question(
            "Neden deforme kanca servis dışı bırakılmadan operasyonda kullanıldı?"
        )
    if any(k in low for k in ("tric", "bilgilendirme")) and any(
        k in low for k in ("katılm", "geç gel", "09:30", "08:00")
    ):
        return enforce_short_why_question(
            "Neden TRIC bilgilendirmesine katılmayan personel kritik göreve alındı?"
        )
    if any(k in low for k in ("sınırlı deneyim", "ikinci kez", "ilk kez")):
        return enforce_short_why_question(
            "Neden sınırlı deneyimli personel yetkinlik doğrulanmadan göreve başlatıldı?"
        )

    sents = _sentences(text) or [text]
    core = sents[0]
    if len(core) < 45 and len(sents) > 1:
        core = f"{sents[0].rstrip('.')} {sents[1]}"

    fragment = core.rstrip(".!?").strip()
    fragment = re.sub(
        r"^(?:Kazazede|kazazede|Garcia|işçi|personel|çalışan)\s+",
        "",
        fragment,
        flags=re.IGNORECASE,
    )

    if re.search(
        r"\b(yd[ıi]|d[üu]|mış|miş|mamış|memiş|madı|medi|dı|di|du|dü|mıştır|miştir|"
        r"lamış|lemiş|takmamış|bağlamış|açıldı|kullanılmamış|gösterilmemiş)\b",
        fragment.lower(),
    ):
        q = f"Neden {fragment}?"
    else:
        q = f"Neden {fragment} oluştu?"

    q = repair_why_question(q)
    if re.search(r"\b\w+\s+oluştu\?\s*$", q, re.IGNORECASE) and len(fragment.split()) <= 3:
        q = enforce_short_why_question(f"Neden {fragment} gerçekleşti?")
    return q


def validate_chain_step(
    level: int,
    question: str,
    answer: str,
    prev_answer: str,
    branch_focus: str,
) -> List[str]:
    """Tek NEDEN adımı kalite sorunları."""
    issues: List[str] = []
    q = str(question or "").strip()
    a = str(answer or "").strip()
    if level == 1:
        if is_invalid_why1_ab_answer(a):
            issues.append("W1 cevabı A/B mekanizma değil (belge/İTA boşluğu)")
        return issues
    if level >= 2 and not is_valid_why_question(q, prev_answer, level=level):
        issues.append(f"W{level} sorusu geçersiz veya önceki cevaptan kopuk")
    drift = topic_drift_violation(f"{q} {a}", branch_focus, level=level)
    if drift:
        issues.append(drift)
    if level >= 2 and prev_answer:
        try:
            from agents.why_chain_quality import answer_repeats_previous
        except ImportError:
            from ..why_chain_quality import answer_repeats_previous
        if answer_repeats_previous(prev_answer, a, threshold=0.72):
            issues.append(f"W{level} cevabı önceki adımı tekrarlıyor")
    return issues


def score_chain_quality_v32(
    chain: List[Dict],
    branch_focus: str = "",
) -> float:
    """V3.2 zincir kalite skoru."""
    try:
        from agents.why_chain_quality import score_chain_quality
    except ImportError:
        from ..why_chain_quality import score_chain_quality

    base = score_chain_quality(chain)
    if len(chain) < 5:
        return base
    penalty = 0.0
    prev_a = ""
    for step in chain:
        lvl = int(step.get("level") or 0)
        q = str(step.get("question_tr") or "")
        a = str(step.get("answer_tr") or "")
        for issue in validate_chain_step(lvl, q, a, prev_a, branch_focus):
            penalty += 0.08
        prev_a = a
    return max(0.35, min(0.98, base - penalty))
