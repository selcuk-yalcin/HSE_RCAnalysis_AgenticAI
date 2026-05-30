from shared.report_i18n import (
    apply_shell_language,
    report_label,
    set_report_lang,
    shell_fallback_replacements,
)


def test_report_label_en_has_no_turkish_shell_headers():
    keys = [
        "section_executive_summary",
        "section_incident_details",
        "section_analysis_method",
        "section_corrective_actions",
        "section_lessons_learned",
        "section_conclusion",
        "section_signatures",
        "nav_toc",
        "toolbar_edit_off",
    ]
    turkish_markers = ("Ö", "ö", "İ", "ı", "Ş", "ş", "Ç", "ç", "Ğ", "ğ", "Ü", "ü")
    for key in keys:
        label = report_label("en", key)
        assert not any(ch in label for ch in turkish_markers), f"{key} leaked TR chars: {label}"


def test_report_label_fallback_to_en_for_unknown_lang():
    assert report_label("de", "cover_title") == report_label("en", "cover_title")


def test_report_label_missing_key_marker():
    assert report_label("en", "nonexistent_key_xyz") == "[missing:nonexistent_key_xyz]"


def test_apply_shell_language_replaces_turkish_nav():
    tr_html = '<button>İçindekiler</button><h3>İÇİNDEKİLER</h3>'
    en_html = apply_shell_language(tr_html, "en")
    assert "Contents" in en_html or "TABLE OF CONTENTS" in en_html
    assert "İçindekiler" not in en_html


def test_shell_fallback_pairs_cover_section_titles():
    pairs = shell_fallback_replacements("en")
    assert pairs.get("YÖNETİCİ ÖZETİ") == "EXECUTIVE SUMMARY"
    assert pairs.get("OLAY BİLGİLERİ") == "INCIDENT DETAILS"


def test_set_report_lang_context():
    set_report_lang("en")
    assert report_label("", "cover_title") == "ROOT CAUSE ANALYSIS REPORT"
    set_report_lang("tr")


def test_html_template_en_shell_no_turkish_headers():
    from agents.skillbased_docx_agent import SkillBasedDocxAgent

    agent = SkillBasedDocxAgent.__new__(SkillBasedDocxAgent)
    content = {
        "cover": {"title": "Test", "ref_no": "1", "date": "2026", "location": "Site"},
        "executive_summary": {"key_findings": [], "immediate_actions": []},
        "incident_details": {"info_table": {}, "event_table": {}, "timeline": []},
        "analysis_method": {"code_system": [], "team_members": []},
        "branches": [],
        "contributing_factors": [],
        "corrective_actions": [],
        "lessons_learned": {},
        "conclusion": {},
    }
    html = agent._generate_html_template(
        content,
        lang={"code": "en", "name": "English", "rtl": False, "html_lang": "en"},
    )
    assert "EXECUTIVE SUMMARY" in html
    assert "YÖNETİCİ ÖZETİ" not in html
    assert "İçindekiler" not in html
    assert "Edit Mode: OFF" in html
