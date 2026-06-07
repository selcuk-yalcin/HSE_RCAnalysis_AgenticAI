"""5-Why kalite kuralları birim testleri."""

from agents.why_chain_quality import (
    SNAP_ROOT_JACCARD_MIN,
    answer_repeats_previous,
    build_why1_question,
    demote_solution_to_cause,
    derive_root_cause_from_why5,
    effective_critic_jaccard_threshold,
    enforce_short_why_question,
    format_barsel_why_answer,
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
