"""Rapor metinlerinden HSG / sınıflandırma kodlarını çıkarma (okuyucuya gösterilmez)."""

from __future__ import annotations

import re

# Parantez içi kodlar: (D4.1), (C3.1 & C3.3), (H-1.5)
_RE_PAREN_CODES = re.compile(
    r"\(\s*(?:\*{0,2})?"
    r"(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?)"
    r"(?:\s*[&,/]\s*(?:\*{0,2})?(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?))*"
    r"\s*\*?\s*\)",
    re.UNICODE,
)

# "Birincil Kod: D9.1 (...)" satırları
_RE_META_KOD_LINES = re.compile(
    r"(?im)^\s*\*?\*?(?:Birincil|İkincil|Üçüncül|Üçüncü)\s+Kod\*?\*?\s*:.*$",
)

_RE_ORPHAN_EMPTY = re.compile(r"\(\s*\)")
_RE_INLINE_CODES = re.compile(
    r"(?i)(?:\*{0,2})\b(?:[A-Z]\d+(?:\.\d+)?|[A-Z]-\d+(?:\.\d+)?)\b(?:\*{0,2})"
)
_RE_CODE_PREFIXES = re.compile(
    r"(?im)\b(?:birincil|ikincil|üçüncül|ucuncul|third|primary|secondary)\s+code\s*:\s*"
)
_RE_DANGLING_SEPARATORS = re.compile(r"\s*[-:;,]\s*$")


def strip_hse_codes(text: str) -> str:
    """Metindeki HSG benzeri kodları ve 'Birincil Kod:' satırlarını kaldırır."""
    if not text or not isinstance(text, str):
        return text
    s = text
    s = _RE_META_KOD_LINES.sub("", s)
    s = _RE_CODE_PREFIXES.sub("", s)
    s = _RE_PAREN_CODES.sub("", s)
    # D1.1 / C3.2 gibi metin içi kodları da temizle (parantez şartı yok).
    s = _RE_INLINE_CODES.sub("", s)
    for _ in range(3):
        s2 = _RE_PAREN_CODES.sub("", s)
        if s2 == s:
            break
        s = s2
    # Kod silme sonrası kalan ayırıcı ve tekrar boşlukları toparla.
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\(\s*[-:;,]?\s*\)", "", s)
    s = re.sub(r"\s*([-:;,])\s*([-:;,])\s*", r"\1 ", s)
    s = re.sub(r"(?m)\s*[-:;,]\s*$", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = _RE_ORPHAN_EMPTY.sub("", s)
    s = _RE_DANGLING_SEPARATORS.sub("", s)
    return s.strip()
