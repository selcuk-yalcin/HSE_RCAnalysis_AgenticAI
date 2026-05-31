from shared.report_delivery_email import build_report_ready_email, normalize_delivery_lang


def test_normalize_delivery_lang():
    assert normalize_delivery_lang("en") == "en"
    assert normalize_delivery_lang("EN-US") == "en"
    assert normalize_delivery_lang("tr") == "tr"
    assert normalize_delivery_lang("") == "tr"


def test_build_email_tr():
    subject, html, plain = build_report_ready_email(
        incident_id="INC-001",
        output_language="tr",
        docx_link="https://example.com/docx",
    )
    assert "hazır" in subject.lower() or "Kök" in subject
    assert "INC-001" in html
    assert "ek" in html.lower() or "eklenmiştir" in html
    assert "INC-001_report.html" in html
    assert "DOCX" in html
    assert "INC-001" in plain


def test_build_email_en():
    subject, html, plain = build_report_ready_email(
        incident_id="INC-002",
        output_language="en",
    )
    assert "report" in subject.lower()
    assert "English" in html
    assert "attached" in html.lower()
    assert "INC-002_report.html" in html
    assert "INC-002" in plain
