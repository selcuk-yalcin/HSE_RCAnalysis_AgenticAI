from shared.report_layout_config import resolve_report_layout, section_label


def test_resolve_report_layout_defaults():
    layout = resolve_report_layout({})
    assert layout["show_technical_codes"] is False
    assert layout["watermark_mode"] in ("none", "draft", "final")
    assert "cover" in layout["sections"]


def test_incident_override_show_codes():
    layout = resolve_report_layout({"report_layout": {"show_technical_codes": True}})
    assert layout["show_technical_codes"] is True


def test_section_label_tr_en():
    assert section_label("cover", "tr") == "Kapak"
    assert section_label("cover", "en") == "Cover"
