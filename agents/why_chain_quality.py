"""5-Why zinciri kalite kuralları: kısa soru, BARSEL etiket, derinleşme, neden dili."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

try:
    from agents.barsel_taxonomy import extract_taxonomy_code, official_title_tr_for_code
except ImportError:
    from .barsel_taxonomy import extract_taxonomy_code, official_title_tr_for_code

WHY_QUESTION_MAX_WORDS = 20

_RE_MULTI_CLAUSE = re.compile(r"\b(ve|ile birlikte|ayrıca|hem\b.*\bhem)\b", re.IGNORECASE)
_RE_BARSSEL_PREFIX = re.compile(
    r"^\s*(?:[ABCD]\d+\.\d+)\s*[—–\-:]+\s*[^:]{3,80}:\s*",
    re.IGNORECASE,
)
_SOLUTION_MARKERS = (
    "verilmeli",
    "yapılmalı",
    "yapılmalıydı",
    "sağlanmalı",
    "uygulanmalı",
    "önlenmeli",
    "alınmalı",
    "düzeltilmeli",
    "gerekir",
    "gerekli kılınmalıydı",
    "zorunlu tutulmalıydı",
    "önerilir",
    "should be",
    "must be",
    "needs to be",
    "shall be",
)
_RE_SOLUTION_PHRASES = re.compile(
    r"\b("
    r"yapılmalıydı|yapılması\s+gerekirdi|gerekli\s+kılınmalıydı|zorunlu\s+tutulmalıydı|"
    r"sağlanmalıydı|uygulanmalıydı|alınmalıydı|önlenmeli(dir)?|düzeltilmeli(dir)?"
    r")\b",
    re.IGNORECASE,
)
_RE_RISK_HAZOP_THEME = re.compile(
    r"\b(hazop|lopa|pha|bowtie|bow\s*tie|iş\s*izni|ptw|"
    r"risk\s*değerlendirme|risk\s*analiz|risk\s*kontrol|jha|jsa)\b",
    re.IGNORECASE,
)
SNAP_ROOT_JACCARD_MIN = 0.12
D4_D5_RISK_CRITIC_JACCARD = 0.42
_SOLUTION_REWRITES = (
    (re.compile(r"\b(eğitim|talimat|prosedür|kkd|izin)\s+verilmelidir\b", re.I), r"\1 verilmemişti"),
    (re.compile(r"\b(eğitim|talimat|prosedür|kkd|izin)\s+verilmeli(dir)?\b", re.I), r"\1 verilmemişti"),
    (re.compile(r"\b(yapılmalıydı|yapılması\s+gerekirdi)\b", re.I), "yapılmamıştı"),
    (re.compile(r"\b(gerekli\s+kılınmalıydı|zorunlu\s+tutulmalıydı)\b", re.I), "tanımlanmamıştı"),
    (re.compile(r"\b(yapılmalı|uygulanmalı|sağlanmalı|alınmalı)(dır|dir)?\b", re.I), "yapılmamıştı"),
    (re.compile(r"\b(önlenmeli|düzeltilmeli)(dir)?\b", re.I), "önlenmemişti"),
)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", str(text or "")))


def _hard_truncate_words(text: str, max_words: int) -> str:
    """LLM yeniden denemesi olmadan kelime sınırında kes."""
    words = re.findall(r"\S+", str(text or "").strip())
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(",;:")


def enforce_short_why_question(question: str, *, max_words: int = WHY_QUESTION_MAX_WORDS) -> str:
    """Tek cümle, en fazla max_words kelime (uzun sorular retry olmadan kırpılır)."""
    q = re.sub(r"\s+", " ", str(question or "").strip())
    if not q:
        return q
    q = q.split("?")[0].strip() + "?"
    parts = re.split(r"[.!]\s+", q.replace("?", ""))
    if parts:
        q = parts[0].strip()
    if not q.endswith("?"):
        q = q.rstrip(".") + "?"
    body = q.replace("?", "").strip()
    if word_count(body) > max_words:
        body = _hard_truncate_words(body, max_words)
        q = body + "?"
    if not q.startswith(("Neden", "neden", "Why", "why")):
        q = "Neden " + q.lstrip("?").strip()
        if not q.endswith("?"):
            q += "?"
    # Son güvence: önek eklendikten sonra da sert kes
    prefix_match = re.match(r"^(Neden|neden|Why|why)\s+", q)
    prefix = prefix_match.group(0) if prefix_match else ""
    rest = q[len(prefix) :].rstrip("?").strip()
    if word_count(prefix + rest) > max_words:
        budget = max(1, max_words - word_count(prefix))
        rest = _hard_truncate_words(rest, budget)
        q = f"{prefix}{rest}?"
    return q


def single_mechanism_text(text: str, *, max_len: int = 160) -> str:
    """Doğrudan neden: tek mekanizma cümlesi."""
    s = str(text or "").strip().split(";")[0].split(" — ")[0].strip()
    if _RE_MULTI_CLAUSE.search(s) and "," in s:
        s = s.split(",")[0].strip()
    if len(s) > max_len:
        s = s[:max_len].rsplit(" ", 1)[0].strip()
    return s


def build_why1_question(immediate_cause: Dict) -> str:
    """Birincil zararlı mekanizmaya tek odaklı Why-1."""
    cause = (
        str(immediate_cause.get("cause_tr") or immediate_cause.get("standard_title_tr") or "")
        .strip()
    )
    cause = cause.split(";")[0].split(" — ")[0].strip()
    if _RE_MULTI_CLAUSE.search(cause) and "," in cause:
        cause = cause.split(",")[0].strip()
    cause = re.sub(r"^(çünkü|neden)\s+", "", cause, flags=re.IGNORECASE).strip()
    if not cause:
        return "Neden birincil zararlı mekanizma oluştu?"
    if cause.lower().startswith("neden"):
        return enforce_short_why_question(cause)
    return enforce_short_why_question(f"Neden {cause.rstrip('.')}?")


def _token_set(text: str) -> set:
    return {
        t
        for t in re.findall(r"[a-z0-9çğıöşü]{4,}", (text or "").lower())
    }


def token_jaccard(a: str, b: str) -> float:
    ta, tb = _token_set(a), _token_set(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def answer_repeats_previous(previous: str, new_answer: str, *, threshold: float = 0.62) -> bool:
    return token_jaccard(previous, new_answer) >= threshold


def question_repeats_answer(answer: str, question: str, *, threshold: float = 0.55) -> bool:
    """Why-2+ sorusu bir önceki cevabı yeniden anlatıyor mu?"""
    q = (question or "").lower()
    a_tokens = _token_set(answer)
    if not a_tokens:
        return False
    q_tokens = _token_set(q)
    if not q_tokens:
        return False
    overlap = len(q_tokens & a_tokens) / max(1, len(q_tokens))
    return overlap >= threshold or token_jaccard(answer, question) >= threshold


def is_solution_language(text: str) -> bool:
    low = (text or "").lower()
    return any(m in low for m in _SOLUTION_MARKERS) or bool(_RE_SOLUTION_PHRASES.search(low))


def _d_subgroup(code: str) -> str:
    key = extract_taxonomy_code(code) or (code or "").strip().upper()
    m = re.match(r"^(D\d+)", key)
    return m.group(1) if m else ""


def is_d4_d5_risk_hazop_branch_pair(code_a: str, code_b: str, text_a: str, text_b: str) -> bool:
    """D4.x ile D5.x dallarında ortak HAZOP/risk teması (yanlış birleştirmeyi önlemek için)."""
    ga, gb = _d_subgroup(code_a), _d_subgroup(code_b)
    if not ga or not gb or ga == gb:
        return False
    if {ga, gb} != {"D4", "D5"}:
        return False
    return bool(_RE_RISK_HAZOP_THEME.search(text_a or "")) and bool(
        _RE_RISK_HAZOP_THEME.search(text_b or "")
    )


def effective_critic_jaccard_threshold(
    code_a: str,
    code_b: str,
    text_a: str,
    text_b: str,
    base_threshold: float,
) -> float:
    """
    D4.x + D5.x HAZOP/risk temalı dallar için daha yüksek eşik (tamamlayıcı açılar korunur).
    Diğer çiftlerde base_threshold (varsayılan 0.25) uygulanır.
    """
    if is_d4_d5_risk_hazop_branch_pair(code_a, code_b, text_a, text_b):
        return max(base_threshold, D4_D5_RISK_CRITIC_JACCARD)
    return base_threshold


def demote_solution_to_cause(text: str) -> str:
    """Öneri/yükümlülük dilini geçmiş olgu diline çevir."""
    s = str(text or "").strip()
    if not s:
        return s
    for pat, repl in _SOLUTION_REWRITES:
        s = pat.sub(repl, s)
    if is_solution_language(s):
        s = re.sub(
            r"\b(için\s+)?(gerekir|gerekli|önerilir|yapılmalı|verilmeli)\b",
            " eksikti",
            s,
            flags=re.IGNORECASE,
        )
    return s.strip()


def strip_barsel_answer_prefix(text: str) -> str:
    return _RE_BARSSEL_PREFIX.sub("", str(text or "").strip()).strip()


def format_barsel_why_answer(code: str, narrative: str) -> str:
    """Her Why cevabı: D4.3 — Resmi başlık: açıklama."""
    key = extract_taxonomy_code(code) or (code or "").strip().upper()
    body = strip_barsel_answer_prefix(demote_solution_to_cause(narrative))
    title = official_title_tr_for_code(key) if key else ""
    if key and title:
        return f"{key} — {title}: {body}"
    if key:
        return f"{key}: {body}"
    return body


def resolve_why_taxonomy_code(raw_code: str, narrative: str, taxonomy_blob: str) -> str:
    """LLM kodunu doğrula; listede yoksa metinden çıkar."""
    code = extract_taxonomy_code(raw_code) or extract_taxonomy_code(narrative)
    if code:
        return code
    for m in re.finditer(r"\b([CD]\d+\.\d+)\b", taxonomy_blob or "", re.IGNORECASE):
        return m.group(1).upper()
    return ""


def pick_non_forbidden_code(
    preferred: str,
    narrative: str,
    taxonomy_blob: str,
    forbidden: List[str],
) -> str:
    code = resolve_why_taxonomy_code(preferred, narrative, taxonomy_blob)
    forbidden_set = {(c or "").strip().upper() for c in (forbidden or []) if c}
    if code and code not in forbidden_set:
        return code
    for m in re.finditer(r"\b([CD]\d+\.\d+)\b", taxonomy_blob or "", re.IGNORECASE):
        cand = m.group(1).upper()
        if cand not in forbidden_set:
            return cand
    return code


def derive_root_cause_from_why5(
    why5: Dict,
    *,
    snap_fn,
    incident_hint: str = "",
    affirmed_typical_problems: Optional[List[str]] = None,
) -> Dict:
    """
    Kök neden: yaprak C/D kodu title + definition/typical_problems açıklaması.
    """
    code = extract_taxonomy_code(why5.get("code")) or str(why5.get("code") or "").strip().upper()
    raw_answer = strip_barsel_answer_prefix(str(why5.get("answer_tr") or ""))
    title = official_title_tr_for_code(code) if code else ""
    snapped = (
        snap_fn(code, raw_answer, raw_answer, family="cd")
        if snap_fn
        else None
    )
    if snapped:
        snap_label = str(
            snapped.get("cause_tr") or snapped.get("standard_title_tr") or ""
        ).strip()
        overlap_text = " ".join(
            x for x in (raw_answer, str(why5.get("question_tr") or "")) if x
        )
        if snap_label and token_jaccard(overlap_text, snap_label) < SNAP_ROOT_JACCARD_MIN:
            snapped = None
    if snapped:
        base = dict(snapped)
    else:
        direct_title = single_mechanism_text(raw_answer, max_len=120) or raw_answer[:120].strip()
        base = {
            "code": code,
            "standard_title_tr": direct_title,
            "cause_tr": direct_title or title,
            "category_type": "ORGANİZASYONEL" if (code or "").startswith("D") else "KİŞİSEL",
            "explanation_tr": raw_answer,
            "confidence": 0.75,
            "snap_rejected": bool(snap_fn),
        }
    try:
        from agents.barsel_taxonomy import enrich_root_cause_from_taxonomy
    except ImportError:
        from .barsel_taxonomy import enrich_root_cause_from_taxonomy

    enriched = enrich_root_cause_from_taxonomy(
        base,
        incident_hint=incident_hint or raw_answer,
        affirmed_typical_problems=affirmed_typical_problems,
    )
    if "confidence" not in enriched and "confidence" in base:
        enriched["confidence"] = base["confidence"]
    return enriched


def score_chain_quality(chain: List[Dict]) -> float:
    if len(chain) < 5:
        return 0.55
    score = 1.0
    for i, step in enumerate(chain):
        q, a = step.get("question_tr", ""), step.get("answer_tr", "")
        if word_count(q) > WHY_QUESTION_MAX_WORDS + 2:
            score -= 0.08
        if not extract_taxonomy_code(step.get("code")) and i >= 0:
            score -= 0.06
        if is_solution_language(a):
            score -= 0.12
        if i > 0:
            prev_a = chain[i - 1].get("answer_tr", "")
            if answer_repeats_previous(prev_a, a):
                score -= 0.15
            if question_repeats_answer(prev_a, q):
                score -= 0.1
    return max(0.35, min(0.98, score))


def branch_diversity_angle(branch_index: int, total: int) -> str:
    """Dallar farklı organizasyonel boyutlara yayılsın."""
    angles = [
        "C — kişisel yetkinlik / davranış / eğitim uygulaması (geçmiş olgu)",
        "D — yönetim ve gözetim sistemleri (geçmiş olgu)",
        "D — teknik tasarım / mühendislik kontrolleri (geçmiş olgu)",
        "D — risk değerlendirme ve iş izni sistemleri (geçmiş olgu)",
        "D — üretim baskısı ve güvenlik kültürü (geçmiş olgu)",
    ]
    return angles[(branch_index - 1) % len(angles)]
