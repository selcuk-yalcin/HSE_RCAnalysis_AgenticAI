"""Rapor metninde markdown ** → HTML kalın / düz metin temizliği."""

from agents.report_text_sanitize import (
    format_report_html_rich,
    sanitize_report_text,
    strip_markdown_emphasis,
)


def test_strip_markdown_emphasis_removes_stars():
    raw = "**1. Finansal Kusur:** Bütçe önceliği operatör davranışına kayıyor."
    assert "**" not in strip_markdown_emphasis(raw)
    assert "1. Finansal Kusur:" in strip_markdown_emphasis(raw)


def test_sanitize_report_text_strips_markdown():
    assert "**" not in sanitize_report_text("**Sonuç:** Üretim baskısı kanıtlandı.")


def test_format_report_html_rich_bold_and_no_raw_stars():
    raw = "**1. ROI:** Hesap yalnızca işgücü.\n**Sonuç:** Kültür zayıf."
    html = format_report_html_rich(raw)
    assert "**" not in html
    assert "<strong>1. ROI:</strong>" in html
    assert 'class="rc-point"' in html
