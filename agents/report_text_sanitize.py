"""Rapor metinlerinden kod, emoji ve İngilizce taksonomi gürültüsünü temizleme."""

from __future__ import annotations

import html as html_module
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
_RE_MD_BOLD = re.compile(r"\*\*([^*]+?)\*\*")
_RE_MD_BOLD_UL = re.compile(r"__([^_]+?)__")
_RE_MD_NUMBERED_POINT = re.compile(
    r"^\s*(?:<strong>)?(\d+)\.\s*(.+?)(?:</strong>)?\s*:?\s*$",
    re.IGNORECASE,
)


def strip_markdown_emphasis(text: str) -> str:
    """Rapor düz metninde ** / __ vurgu işaretlerini kaldırır (içerik kalır)."""
    if not text or not isinstance(text, str):
        return text
    s = str(text)
    s = _RE_MD_BOLD_UL.sub(r"\1", s)
    s = _RE_MD_BOLD.sub(r"\1", s)
    s = re.sub(r"\*+", "", s)
    s = re.sub(r"_+", "", s)
    return s.strip()


def _format_report_text_core(text: str, *, show_technical_codes: bool) -> str:
    """Kod/emoji temizliği; markdown vurgu işaretleri korunur (HTML için)."""
    if not text or not isinstance(text, str):
        return ""
    if show_technical_codes:
        return strip_emojis(text).strip()
    return strip_hse_codes(text)


def _html_emphasis_segments(text: str) -> str:
    """Düz metindeki ** / __ vurgularını kaçışlı HTML <strong> yapar."""
    s = _RE_MD_BOLD_UL.sub(r"**\1**", text or "")
    parts = re.split(r"\*\*([^*]+?)\*\*", s)
    chunks: list[str] = []
    for i, part in enumerate(parts):
        if not part:
            continue
        esc = html_module.escape(part, quote=False)
        if i % 2 == 1:
            chunks.append(f"<strong>{esc}</strong>")
        else:
            chunks.append(esc)
    merged = "".join(chunks)
    return re.sub(r"\*+", "", merged)


def format_report_html_rich(text: str, *, show_technical_codes: bool | None = None) -> str:
    """
    Rapor HTML alanları: sanitize + **kalın** → <strong>, numaralı maddeler vurgulu paragraf.
    Ham ** karakterleri çıktıda kalmaz.
    """
    if not text or not isinstance(text, str):
        return ""
    show = _report_text_show_codes if show_technical_codes is None else show_technical_codes
    base = _format_report_text_core(text, show_technical_codes=show)
    lines = [ln.strip() for ln in base.split("\n") if ln.strip()]
    if not lines:
        return ""

    blocks: list[str] = []
    for ln in lines:
        rich = _html_emphasis_segments(ln)
        plain_probe = re.sub(r"<[^>]+>", "", rich)
        if _RE_MD_NUMBERED_POINT.match(plain_probe) or re.match(r"^\d+\.\s", plain_probe):
            blocks.append(f'<p class="rc-point">{rich}</p>')
        else:
            blocks.append(f'<p class="report-para">{rich}</p>')
    return "\n".join(blocks)


def strip_emojis(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    return _RE_EMOJI.sub("", text)


def strip_hsg_labels(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    return _RE_HSG_WORDS.sub("", text)


_RE_ROOT_CAUSE_LABEL_PREFIX = re.compile(
    r"^(?:KÖK\s*NEDEN|Kök\s*Neden|ROOT\s*CAUSE)\s*(?:\d+\s*)?[:\-–]?\s*",
    re.IGNORECASE,
)


def strip_root_cause_label_prefix(title: str, branch_number: int | None = None) -> str:
    """'Kök Neden 1: …' / 'KÖK NEDEN 1: …' öneklerini kaldırır (şablonda tekrar eklenmesin)."""
    s = strip_hse_codes(str(title or "")).strip()
    if not s:
        return ""
    for _ in range(3):
        m = _RE_ROOT_CAUSE_LABEL_PREFIX.match(s)
        if not m:
            break
        s = s[m.end() :].strip()
    if branch_number is not None:
        s = re.sub(
            rf"^{int(branch_number)}\s*[:\-–]\s*",
            "",
            s,
            flags=re.IGNORECASE,
        ).strip() or s
    return s


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
    Kök neden kutusu için Türkçe başlık: BARSEL JSON tam yaprak adı (kodsuz, kısaltmasız).
    """
    code_key = (code or "").strip().upper()
    try:
        from agents.barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code
    except ImportError:
        from .barsel_taxonomy import barsel_taxonomy_enabled, official_title_tr_for_code

    if code_key and barsel_taxonomy_enabled():
        official = official_title_tr_for_code(code_key)
        if official:
            return strip_hse_codes(official)

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
    return strip_markdown_emphasis(_format_report_text_core(text, show_technical_codes=show))


def sanitize_report_text(text: str) -> str:
    """Tam rapor metni temizliği (kod + emoji + HSG etiketi + EN gürültü + markdown)."""
    return format_report_text(text)
