from shared.report_layout_config import resolve_report_layout, section_label, list_layout_catalog


def test_resolve_report_layout_defaults():
    layout = resolve_report_layout({})
    assert layout["show_technical_codes"] is False
    assert layout["watermark_mode"] in ("none", "draft", "final")
    assert "cover" in layout["sections"]


def test_incident_override_show_codes():
    layout = resolve_report_layout({"report_layout": {"show_technical_codes": True}})
    assert layout["show_technical_codes"] is True


def test_list_layout_catalog():
    catalog = list_layout_catalog("tr")
    assert len(catalog["cover_templates"]) == 4
    assert len(catalog["watermark_options"]) == 3
    assert len(catalog["sections"]) >= 8


def test_normalize_layout_patch():
    from shared.report_layout_config import normalize_layout_patch

    out = normalize_layout_patch({"cover_template": "executive", "watermark_mode": "draft"})
    assert out["cover_template"] == "executive"
    assert out["watermark_mode"] == "draft"
