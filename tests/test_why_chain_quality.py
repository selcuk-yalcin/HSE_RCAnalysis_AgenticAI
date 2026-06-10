"""5-Why kalite kuralları birim testleri."""

from agents.why_chain_quality import (
    SNAP_ROOT_AUDIT_MIN,
    SNAP_ROOT_JACCARD_MIN,
    answer_repeats_previous,
    branch_diversity_angle,
    build_event_why1_question,
    build_why1_question,
    demote_solution_to_cause,
    derive_root_cause_from_why5,
    effective_critic_jaccard_threshold,
    enforce_short_why_question,
    format_barsel_why_answer,
    immediate_cause_sentence,
    is_solution_language,
    pick_non_forbidden_code,
    single_mechanism_text,
    word_count,
)


def test_enforce_short_why_question_max_words():
    long_q = "Neden " + " ".join(["kelime"] * 30) + "?"
    short = enforce_short_why_question(long_q)
    assert word_count(short) <= 20
    assert short.endswith("?")


def test_build_why1_single_mechanism():
    q = build_why1_question(
        {"cause_tr": "Makine çalışırken müdahale edildi; prosedür ihlali ve eğitim eksikliği"}
    )
    assert word_count(q) <= 20
    assert "prosedür" not in q.lower() or "müdahale" in q.lower()


def test_build_why1_asks_sub_mechanism_not_circular():
    # P1.23-G1: Soru doğrudan nedeni "neden oldu" diye değil alt mekanizma olarak sormalı.
    q = build_why1_question({"cause_tr": "keskin talaşa doğrudan temas"})
    assert word_count(q) <= 20
    assert "alt mekanizma" in q.lower()


def test_build_event_why1_question_targets_event():
    # P1.24: Why-1 olayın kendisine sorulur; cevabı doğrudan neden olacaktır.
    incident = (
        "Üretim hattındaki bir ekipmanda kontaktörün yapışık kalması sonucu "
        "ısı yükselmesi ve dumanlama meydana gelmiştir. Rezistanslarda yanık yoktur."
    )
    q = build_event_why1_question(incident)
    assert q.startswith("Neden ")
    assert q.endswith("meydana geldi?")
    # Olay cümlesinin sonundaki "meydana gelmiştir" kuyruğu çiftlenmemeli.
    assert "gelmiştir" not in q


def test_build_event_why1_question_skips_instruction_blocks():
    incident = (
        "[Instruction: produce analysis text in English where applicable]\n"
        "Konveyör bandında yatak arızası nedeniyle duruş yaşanmıştır."
    )
    q = build_event_why1_question(incident)
    assert "Instruction" not in q
    assert q.startswith("Neden ")


def test_build_event_why1_question_empty_fallback():
    assert build_event_why1_question("") == "Neden bu olay meydana geldi?"


def test_immediate_cause_sentence_completes_fragment():
    # Düşük (yarım) cümle tam cümleye çevrilmeli.
    frag = "Kontaktörün zamanla eskimesi nedeniyle yapışık kalması"
    out = immediate_cause_sentence(frag)
    assert out.endswith("olayın doğrudan nedenidir.")
    assert out.startswith("Kontaktörün")


def test_immediate_cause_sentence_keeps_full_sentence():
    full = "Kontaktör yapışık kalmıştır."
    assert immediate_cause_sentence(full) == full


def test_format_barsel_why_answer_includes_code_and_title():
    out = format_barsel_why_answer("D4.3", "Bütçe önceliği operatör davranışına kayıyor.")
    assert out.startswith("D4.3")
    assert "—" in out
    assert "verilmemişti" not in out or "D4.3" in out


def test_demote_solution_language():
    assert is_solution_language("Eğitim verilmelidir.")
    assert is_solution_language("Saha davranış doğrulaması yapılmalıydı.")
    assert is_solution_language("Prosedür gerekli kılınmalıydı.")
    assert is_solution_language("KKD kullanımı zorunlu tutulmalıydı.")
    fixed = demote_solution_to_cause("Eğitim verilmelidir.")
    assert "verilmemiş" in fixed.lower()


def test_enforce_short_why_question_hard_truncates_without_retry_needed():
    long_q = "Neden " + " ".join([f"kelime{i}" for i in range(40)]) + "?"
    short = enforce_short_why_question(long_q)
    assert word_count(short) <= 20
    assert short.startswith("Neden")


def test_derive_root_cause_rejects_low_jaccard_snap():
    why5 = {
        "code": "D1.4",
        "answer_tr": "Üretim hedefi bakım penceresini daralttı ve sensör yatırımı ertelendi.",
    }

    def bad_snap(*_a, **_k):
        return {
            "code": "D8.4",
            "cause_tr": "Malzeme depolama yetersizliği",
            "standard_title_tr": "Malzeme depolama yetersizliği",
        }

    out = derive_root_cause_from_why5(why5, snap_fn=bad_snap)
    assert out.get("snap_rejected") is True
    assert "üretim hedefi" in str(out.get("cause_tr") or "").lower()
    assert SNAP_ROOT_JACCARD_MIN == 0.12


def test_d4_d5_risk_pair_uses_higher_critic_threshold():
    thr = effective_critic_jaccard_threshold(
        "D4.1",
        "D5.7",
        "risk değerlendirme ve iş izni süreci eksikti",
        "HAZOP analizi yapılmamış ve tasarım riskleri gözden geçirilmemişti",
        0.25,
    )
    assert thr >= 0.42
    thr_plain = effective_critic_jaccard_threshold(
        "D1.2",
        "D3.2",
        "gözetim yetersizdi",
        "eğitim verilmemişti",
        0.25,
    )
    assert thr_plain == 0.25


def test_answer_repeats_previous_detects_copy():
    prev = "Üretim hedefi bakım penceresini daralttı ve sensör yatırımı ertelendi."
    dup = "Üretim hedefi bakım penceresini daralttı; sensör yatırımı ertelendi."
    assert answer_repeats_previous(prev, dup)


def test_pick_non_forbidden_code():
    blob = "D4.3 foo D1.4 bar"
    assert pick_non_forbidden_code("D4.3", "", blob, ["D4.3"]) in ("D1.4", "D4.3")


def test_single_mechanism_text_truncates():
    s = single_mechanism_text("A; B ve C, D")
    assert ";" not in s


def test_snap_audit_records_jaccard_and_overrides_unrelated_title():
    # P1.23-G2: Atanan BARSEL resmi başlığı W5 ile alakasızsa (jaccard < 0.08) override.
    why5 = {
        "code": "D4.1",
        "answer_tr": "Vana elle aşırı zorlanarak açıldı ve conta yırtıldı.",
        "question_tr": "Neden conta hasarlandı?",
    }

    def unrelated_snap(*_a, **_k):
        return {
            "code": "D4.1",
            "cause_tr": "Risk değerlendirme süreci eksikliği",
            "standard_title_tr": "Risk değerlendirme süreci eksikliği",
            "explanation_tr": "x",
        }

    out = derive_root_cause_from_why5(why5, snap_fn=unrelated_snap)
    assert out.get("snap_overridden") is True
    assert out.get("snap_rejected") is True
    assert "snap_audit_jaccard" in out
    assert out["snap_audit_jaccard"] < SNAP_ROOT_AUDIT_MIN
    assert SNAP_ROOT_AUDIT_MIN == 0.08


def test_snap_kept_when_official_title_overlaps_chain():
    # Resmi başlık W5 ile örtüşürse snap korunur, override olmaz.
    why5 = {
        "code": "D4.1",
        "answer_tr": "Risk değerlendirme süreci yapılmadığı için tehlike fark edilmedi.",
        "question_tr": "Neden tehlike fark edilmedi?",
    }

    def overlapping_snap(*_a, **_k):
        return {
            "code": "D4.1",
            "cause_tr": "Risk değerlendirme yapılmamış",
            "standard_title_tr": "Risk değerlendirme süreci eksikliği",
            "explanation_tr": "x",
        }

    out = derive_root_cause_from_why5(why5, snap_fn=overlapping_snap)
    assert not out.get("snap_overridden")
    assert out.get("snap_audit_jaccard", 0.0) >= SNAP_ROOT_AUDIT_MIN


def test_branch_diversity_angle_skips_risk_when_d4_used():
    # P1.23-G3: D4 zaten kullanıldıysa "risk değerlendirme" açısı önerilmez.
    angle = branch_diversity_angle(4, 5, used_codes=["D4.1"])
    assert "risk değerlendirme" not in angle.lower()
    # used_codes verilmezse eski davranış (rotasyon) korunur.
    plain = branch_diversity_angle(4, 5)
    assert "risk değerlendirme" in plain.lower()
