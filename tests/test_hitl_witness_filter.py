"""HITL — manuel formda tanık varsa tekrar sorulmaması."""

from agents.hitl_question_service import _filter_questions


def test_witness_question_skipped_when_known_field():
    questions = [
        {
            "id": "w1",
            "soru": "Görgü tanıkları olayı nasıl anlattı?",
        },
        {
            "id": "k1",
            "soru": "Bu olayda üretim baskısı güvenlik kararlarını etkiledi mi?",
        },
    ]
    out = _filter_questions(
        questions,
        known_fields=["witness_known"],
        incident_context="Olay anlatımı",
    )
    assert len(out) == 1
    assert "tanık" not in out[0]["soru"].lower()


def test_witness_question_skipped_when_context_has_witness_block():
    questions = [
        {"id": "w1", "soru": "Görgü tanıkları olayı nasıl anlattı?"},
    ]
    ctx = "Olay metni\n\nTaniklar:\n- Ali (Formen): Baskı vardı"
    out = _filter_questions(questions, known_fields=[], incident_context=ctx)
    assert out == []
