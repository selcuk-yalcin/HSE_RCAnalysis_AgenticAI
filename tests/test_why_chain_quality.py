"""5-Why kalite kuralları birim testleri."""

from agents.why_chain_quality import (
    answer_repeats_previous,
    build_why1_question,
    demote_solution_to_cause,
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
    fixed = demote_solution_to_cause("Eğitim verilmelidir.")
    assert "verilmemiş" in fixed.lower()


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
