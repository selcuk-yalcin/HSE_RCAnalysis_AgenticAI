"""V3.2 5-Why zincir kalite kuralları (global, LLM yok)."""

from agents.v3_2.why_chain_quality_v3_2 import (
    build_why2_from_ab_answer,
    is_invalid_why1_ab_answer,
    is_valid_why_question,
    repair_why_question,
    resolve_branch_focus,
    topic_drift_violation,
    validate_chain_step,
)

KF2_W1_ANSWER = (
    "Kazazede emniyet kemerini yük altında bulunan ankraj bloğuna bağlamış; "
    "bağlantının ayrılması sonucu korunasız şekilde düşmüştür."
)

KF3_BAD_W1 = (
    "İş Tehlike Analizi ve yapım metotları incelemesinde sabit ankraja bağlanma "
    "kuralı mevcut olmasına rağmen, ince ayar sırasında rehberlik eksikliği belirlenmiştir."
)

KF1_W4_BAD = (
    "Kaldırma ekipmanları için planlı muayele sorumluluğu kim tarafından tanımlanmamıştır?"
)


def test_why2_not_emniyet_kemeri_olustu():
    q = build_why2_from_ab_answer(KF2_W1_ANSWER, "supervision_leadership")
    assert "oluştu" not in q.lower() or "emniyet kemeri oluştu" not in q.lower()
    assert q.startswith("Neden ")
    assert "?" in q
    assert "emniyet" in q.lower() or "ankraj" in q.lower() or "süpervizör" in q.lower()


def test_rejects_organizational_w1_answer():
    assert is_invalid_why1_ab_answer(KF3_BAD_W1) is True
    assert is_invalid_why1_ab_answer(KF2_W1_ANSWER) is False


def test_repair_statement_to_neden_question():
    fixed = repair_why_question(KF1_W4_BAD)
    assert fixed.lower().startswith("neden ")
    assert fixed.endswith("?")


def test_rejects_var_miydi_question():
    bad = "Neden Kaldırma ekipmanlarının muayene prosedürü var mıydı?"
    fixed = repair_why_question(bad)
    assert "var mıydı" not in fixed.lower()
    assert fixed.lower().startswith("neden ")
    assert "yoktu" in fixed.lower()


def test_supervision_branch_focus():
    imm = {
        "code": "A2.1",
        "cause_tr": "Süpervizör sözlü uyarı yaptı",
        "evidence_tr": "Ankraj noktası gösterilmedi ve doğrulanmadı.",
    }
    focus_id, prompt = resolve_branch_focus(imm, branch_index=2)
    assert focus_id == "supervision_leadership"
    assert "gözetim" in prompt.lower() or "süpervizör" in prompt.lower()


def test_competence_branch_rejects_mandal_drift():
    drift = topic_drift_violation(
        "Kaldırma ekipmanının mandal deformasyonu neden yakalanmadı?",
        "competence_workforce",
        level=4,
    )
    assert drift is not None


def test_validate_chain_detects_w1_document_gap():
    issues = validate_chain_step(1, "Neden Garcia yaralandı?", KF3_BAD_W1, "", "")
    assert any("W1" in i for i in issues)


def test_causal_link_w2_from_w1():
    q = build_why2_from_ab_answer(KF2_W1_ANSWER)
    assert is_valid_why_question(q, KF2_W1_ANSWER, level=2) is True
