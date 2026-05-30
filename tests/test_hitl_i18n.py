from agents.hitl_question_service import _shape_question, next_hitl_questions
from shared.hitl_i18n import (
    has_turkish_chars,
    normalize_hitl_lang,
    question_batch_has_language_drift,
    safe_fallback_question,
    shape_bilingual_question_fields,
)


def test_normalize_hitl_lang():
    assert normalize_hitl_lang("en-US") == "en"
    assert normalize_hitl_lang("tr") == "tr"
    assert normalize_hitl_lang("") == "tr"


def test_shape_question_en_uses_distinct_question_en():
    row = {
        "id": "d-test",
        "source": "disambiguation",
        "code": "B4.4",
        "cause_desc": "B4.4",
        "hsg245": "D4.1",
        "soru": "Çalışma yapılan yerde bariyer, korkuluk veya güvenlik ağı mevcut muydu?",
        "yönler": {},
    }
    shaped = _shape_question(row, "en")
    assert shaped["question_en"]
    assert shaped["question_tr"]
    assert not has_turkish_chars(shaped["question_en"])
    assert shaped["response_guidance"]
    assert shaped["helper_hint"]


def test_shape_question_tr_keeps_turkish():
    row = {
        "id": "d-test-tr",
        "source": "disambiguation",
        "code": "B4.4",
        "cause_desc": "B4.4",
        "hsg245": "D4.1",
        "soru": "Risk değerlendirmesi yapılmış mıydı?",
        "yönler": {},
    }
    shaped = _shape_question(row, "tr")
    assert has_turkish_chars(shaped["question_tr"])
    assert shaped["question_en"] or shaped["question_tr"]


def test_bilingual_fields_prefers_existing_en():
    tr, en = shape_bilingual_question_fields(
        "Olay hangi saatte oldu?",
        "At what time did the incident occur?",
        "en",
        source="taxonomy_gap",
    )
    assert en == "At what time did the incident occur?"
    assert tr == "Olay hangi saatte oldu?"


def test_language_drift_detection_en_batch():
    batch = [{"question_tr": "TR", "question_en": "Çalışma yapılan yerde bariyer var mıydı?"}]
    assert question_batch_has_language_drift(batch, "en") is True
    batch_ok = [{"question_tr": "TR", "question_en": "Was a barrier present at the work area?"}]
    assert question_batch_has_language_drift(batch_ok, "en") is False


def test_next_hitl_questions_en_batch_no_turkish_display():
    result = next_hitl_questions(
        how_happened="Worker fell from scaffold during maintenance.",
        root_cause_initial="B4.4 — missing guardrail",
        answered_ids=[],
        immediate_causes=[{"code": "B4.4", "cause_tr": "Fall from height"}],
        batch_size=1,
        output_language="en",
    )
    assert result.get("output_language") == "en"
    questions = result.get("questions") or []
    if questions:
        q = questions[0]
        display = q.get("question_en") or ""
        assert not has_turkish_chars(display)
        assert not question_batch_has_language_drift(questions, "en")


def test_safe_fallback_not_opposite_language():
    en = safe_fallback_question("en", "disambiguation")
    tr = safe_fallback_question("tr", "disambiguation")
    assert not has_turkish_chars(en)
    assert has_turkish_chars(tr)
