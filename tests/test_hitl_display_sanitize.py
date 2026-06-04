"""HITL kullanıcıya gösterilen soru metni — kod gizleme."""

from agents.hitl_question_service import _build_deep_questions_from_barsel_taxonomy, _shape_question
from shared.hitl_i18n import sanitize_hsg_hint_for_display, strip_taxonomy_codes_for_display


def test_strip_code_prefix_from_question():
    raw = (
        "A4.3 (Inappropriate/Unsafe Workplace Behavior) icin: "
        "Deliberate unsafe behavior Bu olayda sahaya ne kadar uyuyordu?"
    )
    clean = strip_taxonomy_codes_for_display(raw)
    assert "A4.3" not in clean
    assert "Deliberate" in clean or "geçerli" in clean.lower()


def test_sanitize_hsg_hint_hides_code_list():
    hint = "A2.1 (Uygunsuz kullanım), D5.1 (Yanlış ekipman seçimi)"
    assert sanitize_hsg_hint_for_display(hint) == ""


def test_shape_question_hides_codes_by_default(monkeypatch):
    monkeypatch.delenv("HITL_SHOW_TAXONOMY_CODES", raising=False)
    q = _shape_question(
        {
            "id": "t1",
            "source": "taxonomy_gap",
            "hsg245": "A2.1 (Uygunsuz kullanım), D5.1 (Yanlış ekipman seçimi)",
            "soru": "Hangi ekipman/alet kullanıldı? Amacına uygun muydu?",
            "code": "A2.1",
        },
        "tr",
    )
    assert "A2.1" not in q["question_tr"]
    assert q["hsg_hint"] == ""
    assert "ekipman" in q["question_tr"].lower()


def test_barsel_deep_question_has_no_code_in_soru():
    from agents.barsel_taxonomy import BarselTaxonomyItem

    item = BarselTaxonomyItem(
        code="A1.1",
        title="Bireysel Kural İhlali",
        typical_problems=["Kural ihlalinin görmezden gelinmiş olması"],
        keywords=["kural"],
        section_ids=["A", "A1"],
    )
    import agents.hitl_question_service as svc

    svc._BARSEL_BY_CODE["A1.1"] = item
    rows = _build_deep_questions_from_barsel_taxonomy("A1.1", 1, "kural ihlali")
    assert rows
    assert "A1.1" not in rows[0]["soru"]
    assert "geçerli" in rows[0]["soru"].lower() or "durum" in rows[0]["soru"].lower()
