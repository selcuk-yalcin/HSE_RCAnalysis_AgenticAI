"""P1.22: Kök neden aday (C/D) probe — aday havuzu + cevap semantiği + uçtan uca akış."""

from agents.barsel_taxonomy import (
    derive_hitl_root_signals,
    probe_answer_affirms_fit,
    probe_answer_denies_fit,
    root_cause_candidate_codes,
)
from agents.hitl_question_service import next_root_cause_probe_questions


# Konveyörde "bozulana kadar çalıştır" — yanlış bakım stratejisi (D6.7) senaryosu.
CONVEYOR_INCIDENT = (
    "Yük taşıma konveyöründe yatak arızası nedeniyle duruş yaşandı. Ekipman için "
    "'bozulana kadar çalıştır' stratejisi uygulanıyordu; planlı ve koşul bazlı bakım "
    "reddedilmişti. Yatak için sadece sıcaklık takip ediliyor, titreşim hiç izlenmiyordu. "
    "Güvenlik interlockları için tanımlı bir test/bakım aktivitesi yoktu."
)


def _auto_answer_as_expert(code: str) -> str:
    """
    HITL sorularını 'uzman gibi' otomatik yanıtla:
    - Risk değerlendirme / iş izni (D4.x) kodları bu olaya UYMUYOR → Hayır
    - Diğer (spesifik) C/D adayları → Evet
    """
    return "hayır" if code.upper().startswith("D4") else "evet"


def test_probe_answer_denies_fit_only_explicit_no():
    assert probe_answer_denies_fit("hayır") is True
    assert probe_answer_denies_fit("Hayir") is True
    assert probe_answer_denies_fit("no") is True
    assert probe_answer_denies_fit("uygun değil") is True
    assert probe_answer_denies_fit("bu durum geçerli değil") is True
    # Belirsiz / olumlu / boş → dışlama YOK (yanlış dışlamayı önler)
    assert probe_answer_denies_fit("evet") is False
    assert probe_answer_denies_fit("bilinmiyor") is False
    assert probe_answer_denies_fit("") is False
    assert probe_answer_denies_fit("emin değilim") is False
    assert probe_answer_denies_fit("belki olabilir") is False


def test_probe_answer_affirms_and_denies_are_consistent():
    # Aynı cevap hem affirm hem deny olamaz.
    for ans in ("evet", "hayır", "uygun", "uygun değil", "bilinmiyor", ""):
        assert not (probe_answer_affirms_fit(ans) and probe_answer_denies_fit(ans))


def test_root_cause_candidate_codes_returns_cd_with_group_diversity():
    # retriever=None → saf keyword skoru, makineden bağımsız (deterministik).
    codes = root_cause_candidate_codes(CONVEYOR_INCIDENT, "B2.1", None, max_codes=6, max_per_group=2)
    assert codes, "aday kod havuzu boş olmamalı"
    # Yalnızca C/D bandı
    assert all(c[0] in ("C", "D") for c in codes)
    # Bu olay yanlış bakım stratejisi → D6.7 keyword skoruyla aday havuzunda olmalı.
    assert "D6.7" in codes
    # Grup çeşitliliği: aynı gruptan en fazla 2
    from agents.barsel_taxonomy import group_id_from_code

    groups: dict[str, int] = {}
    for c in codes:
        g = group_id_from_code(c) or c
        groups[g] = groups.get(g, 0) + 1
    assert all(v <= 2 for v in groups.values())


def test_root_cause_candidate_codes_empty_incident():
    assert root_cause_candidate_codes("", "B2.1", None) == []


def test_derive_hitl_root_signals_no_excludes_yes_affirms():
    # Doğrudan sinyal çıkarımı (motor wiring'iyle aynı fonksiyon).
    answers = [
        {"code": "D4.1", "answer": "hayır"},  # risk değerlendirme → bu olaya uymuyor
        {"code": "D6.7", "answer": "evet", "probe_context": "bozulana kadar çalıştır stratejisi"},
        {"code": "D6.1", "answer": "bilinmiyor"},  # belirsiz → etkisiz
    ]
    forbidden, affirmed, texts = derive_hitl_root_signals(answers)
    assert "D4.1" in forbidden
    assert "D6.7" in affirmed
    assert "D6.1" not in forbidden and "D6.1" not in affirmed  # belirsiz nötr
    assert any("bozulana kadar" in t for t in texts)


def test_derive_hitl_root_signals_extracts_code_from_noisy_field():
    answers = [{"code": "[D6.7] Yanlış bakım tipi", "answer": "no"}]
    forbidden, affirmed, _ = derive_hitl_root_signals(answers)
    assert forbidden == ["D6.7"]


def test_end_to_end_root_cause_probe_flow_self_answered():
    """
    Uçtan uca: olay → kök neden aday probe soruları üret → kendim cevapla →
    forbidden/affirmed sinyaline dönüştür. (dspy gerektiren 5-Why motoru hariç.)
    """
    result = next_root_cause_probe_questions(
        how_happened=CONVEYOR_INCIDENT,
        root_cause_initial="",
        answered_ids=[],
        immediate_code="B2.1",
        batch_size=10,
        output_language="tr",
        tenant_id="",
        incident_id="",
    )
    questions = result.get("questions") or []
    candidate_codes = result.get("candidate_codes") or []

    print("\n=== HITL KÖK NEDEN ADAY PROBE — UÇTAN UCA DENEME ===")
    print(f"Aday kodlar: {candidate_codes}")
    assert candidate_codes, "aday kod havuzu boş olmamalı"
    # Yalnızca C/D bandı (D6.7 gibi spesifik kod retriever durumuna göre değişebilir;
    # deterministik D6.7 kontrolü retriever=None testinde yapılır).
    assert all(c[0] in ("C", "D") for c in candidate_codes)

    # HITL sorularını 'uzman gibi' kendim cevaplıyorum.
    probe_answers = []
    for q in questions:
        code = str(q.get("code") or "")
        ans = _auto_answer_as_expert(code)
        ctx = str(q.get("probe_context") or "")
        print(f"\n[{code}] Soru: {q.get('question_tr') or q.get('soru')}")
        if ctx:
            print(f"    İncelenen koşul: {ctx[:120]}")
        print(f"    >> Cevabım: {ans}")
        probe_answers.append({"code": code, "answer": ans, "probe_context": ctx})

    forbidden, affirmed, affirmed_texts = derive_hitl_root_signals(probe_answers)
    print(f"\nMOTORA GİDEN SİNYAL → forbidden={forbidden} | affirmed={affirmed}")

    answered_codes = [str(q.get("code") or "") for q in questions if q.get("code")]
    assert answered_codes, "üretilen sorular kod taşımalı"
    # 'Evet' dediğim spesifik kodlar affirmed'e, D4.x 'Hayır'lar forbidden'a düşmeli.
    for code in answered_codes:
        if code.upper().startswith("D4"):
            assert code in forbidden
        else:
            assert code in affirmed
    # D6.7'ye Evet dedim → kök neden seçiminde tercih edilecek.
    assert "D6.7" in affirmed
    print("\n✅ HITL → kök neden sinyali doğrulandı (D4 dışlandı, D6.7 onaylandı).")
