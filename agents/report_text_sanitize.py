"""Rapor metinlerinden kod, emoji ve İngilizce taksonomi gürültüsünü temizleme."""

from __future__ import annotations

import re

def _load_title_tr_for_code():
    import importlib.util
    from pathlib import Path

    map_path = Path(__file__).resolve().parent / "taxonomy_title_tr_map.py"
    spec = importlib.util.spec_from_file_location("taxonomy_title_tr_map", map_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.title_tr_for_code


try:
    from .taxonomy_title_tr_map import title_tr_for_code
except ImportError:
    try:
        from agents.taxonomy_title_tr_map import title_tr_for_code
    except ImportError:
        title_tr_for_code = _load_title_tr_for_code()

# Parantez içi kodlar: (D4.1), (C3.1 & C3.3), (HSG 12.1)
_RE_PAREN_CODES = re.compile(
    r"\(\s*(?:\*{0,2})?"
    r"(?:HSG|HGS|HSG245)?\s*"
    r"(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?)"
    r"(?:\s*[&,/]\s*(?:\*{0,2})?(?:HSG|HGS)?\s*(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?))*"
    r"\s*\*?\s*\)",
    re.UNICODE | re.IGNORECASE,
)

_RE_META_KOD_LINES = re.compile(
    r"(?im)^\s*\*?\*?(?:Birincil|İkincil|Üçüncül|Üçüncü)\s+Kod\*?\*?\s*:.*$",
)

# Uzun olay metninde rapor özeti dışı bölümleri ayırır (Acil önlemler, kök neden vb.)
_EVENT_SUMMARY_SECTION_MARKERS = (
    "Acil Önlemler",
    "Acil önlemler",
    "Ek Notlar",
    "Ek notlar",
    "Kök Neden",
    "Kök neden",
    "Düzeltici Aksiyon",
    "Düzeltici aksiyon",
    "Emergency Measures",
    "Root Cause",
    "Corrective Action",
)


def full_incident_narrative_for_tree(text: str) -> str:
    """Karar ağacı OLAY kutusu: ek bölümleri keser, olay anlatımının tamamını korur."""
    if not text:
        return ""
    raw = str(text).strip()
    cut_at = len(raw)
    for marker in _EVENT_SUMMARY_SECTION_MARKERS:
        idx = raw.find(marker)
        if idx > 80:
            cut_at = min(cut_at, idx)
    lower = raw.lower()
    for marker in (
        "acil önlemler:",
        "ek notlar:",
        "kök neden (ilk değerlendirme):",
        "düzeltici aksiyon",
        "hitl",
        "[ v s ]",
    ):
        idx = lower.find(marker)
        if idx > 80:
            cut_at = min(cut_at, idx)
    return raw[:cut_at].strip()


def short_incident_summary(text: str, max_chars: int = 360) -> str:
    """Yalnızca olay özetini döndürür; ek bölümleri ve fazla uzunluğu keser."""
    if not text:
        return ""
    raw = str(text).strip()
    cut_at = len(raw)
    for marker in _EVENT_SUMMARY_SECTION_MARKERS:
        idx = raw.find(marker)
        if idx > 80:
            cut_at = min(cut_at, idx)
    summary = raw[:cut_at].strip()
    if len(summary) > max_chars:
        truncated = summary[:max_chars]
        last_stop = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
        if last_stop > int(max_chars * 0.45):
            summary = truncated[: last_stop + 1].strip()
        else:
            summary = truncated.rstrip() + "…"
    return summary

_RE_ORPHAN_EMPTY = re.compile(r"\(\s*\)")
_RE_INLINE_CODES = re.compile(
    r"(?i)(?:\*{0,2})\b(?:HSG|HGS|HSG245)?\s*(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?)\b(?:\*{0,2})"
)
_RE_CODE_PREFIXES = re.compile(
    r"(?im)\b(?:birincil|ikincil|üçüncül|ucuncul|third|primary|secondary)\s+code\s*:\s*"
)
_RE_DANGLING_SEPARATORS = re.compile(r"\s*[-:;,]\s*$")
_RE_HSG_WORDS = re.compile(r"\b(?:HSG\s*245|HSG245|HSG|HGS)\b", re.IGNORECASE)
_RE_EMOJI = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U00002600-\U000026FF"
    "⚠️⚠🚨✅❌🔴🔗📋📊🎯🔀🔧⭐"
    "]+",
    flags=re.UNICODE,
)
_RE_EN_LABELS = re.compile(
    r"(?i)\b(?:CRITICAL|USE VERY CAREFULLY|IMPORTANT DISTINCTION)\b[:\s-]*"
)
# Başta İngilizce kök neden başlığı + ayırıcı (ör. "Training Not Provided - açıklama")
_RE_LEADING_EN_TITLE = re.compile(
    r"^(?:Training Not Provided|Production Pressure|Monitoring/Audit Inadequate|"
    r"Risk Assessment Inadequate|Inadequate Supervision|Weak Leadership Commitment)"
    r"\s*[-–—:]\s*",
    re.IGNORECASE,
)


def strip_emojis(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    return _RE_EMOJI.sub("", text)


def strip_hsg_labels(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    return _RE_HSG_WORDS.sub("", text)


def strip_hse_codes(text: str) -> str:
    """Metindeki sınıflandırma kodlarını ve kod satırlarını kaldırır."""
    if not text or not isinstance(text, str):
        return text
    s = strip_emojis(text)
    s = _RE_META_KOD_LINES.sub("", s)
    s = _RE_CODE_PREFIXES.sub("", s)
    s = _RE_PAREN_CODES.sub("", s)
    s = _RE_INLINE_CODES.sub("", s)
    s = strip_hsg_labels(s)
    for _ in range(3):
        s2 = _RE_PAREN_CODES.sub("", s)
        if s2 == s:
            break
        s = s2
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\(\s*[-:;,]?\s*\)", "", s)
    s = re.sub(r"\s*([-:;,])\s*([-:;,])\s*", r"\1 ", s)
    s = re.sub(r"(?m)\s*[-:;,]\s*$", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = _RE_ORPHAN_EMPTY.sub("", s)
    s = _RE_DANGLING_SEPARATORS.sub("", s)
    s = _RE_EN_LABELS.sub("", s)
    s = _RE_LEADING_EN_TITLE.sub("", s)
    return s.strip()


def taxonomy_display_title(code: str = "", title_en: str = "", cause_tr: str = "") -> str:
    """
    Kök neden kutusu için Türkçe başlık: önce BARSEL/resmi kod haritası, sonra temizlenmiş cause_tr.
    """
    code_key = (code or "").strip().upper()
    mapped = title_tr_for_code(code_key, "")
    if mapped:
        return strip_hse_codes(mapped)

    for candidate in (cause_tr, title_en):
        cleaned = strip_hse_codes(str(candidate or ""))
        if cleaned and not _looks_like_english_taxonomy_title(cleaned):
            return cleaned

    fallback = strip_hse_codes(title_en or cause_tr or "")
    if code_key:
        return title_tr_for_code(code_key, fallback) or fallback or "Kök neden"
    return fallback or "Kök neden"


def _looks_like_english_taxonomy_title(text: str) -> bool:
    """Basit sezgisel: bilinen İngilizce kök neden kalıpları."""
    low = (text or "").lower()
    markers = (
        "training not",
        "production pressure",
        "monitoring/audit",
        "inadequate",
        "ineffective",
        "failure",
        "not provided",
        "weak ",
        "lack of",
    )
    return any(m in low for m in markers) and not any(
        ch in text for ch in "çğıöşüÇĞİÖŞÜ"
    )


_report_text_show_codes: bool = False


def set_report_text_policy(*, show_technical_codes: bool = False) -> None:
    """Thread-local policy for P0.9 code visibility (used during report generation)."""
    global _report_text_show_codes
    _report_text_show_codes = bool(show_technical_codes)


def format_report_text(text: str, *, show_technical_codes: bool | None = None) -> str:
    """Apply export text policy. When show_technical_codes=True, keep taxonomy codes."""
    show = _report_text_show_codes if show_technical_codes is None else show_technical_codes
    if not text or not isinstance(text, str):
        return text
    if show:
        return strip_emojis(text).strip()
    return strip_hse_codes(text)


def sanitize_report_text(text: str) -> str:
    """Tam rapor metni temizliği (kod + emoji + HSG etiketi + EN gürültü)."""
    return format_report_text(text)
