"""HITL probe soru kalıpları — bağlam ayrımı."""

from agents.hitl_question_service import (
    _build_deep_questions_from_barsel_taxonomy,
    _probe_dedup_key,
    _shape_question,
    _should_skip_probe_row,
    build_why_probe_question_pool,
)
from agents.barsel_taxonomy import BarselTaxonomyItem
from shared.hitl_i18n import probe_question_for_type


FIXTURE = BarselTaxonomyItem(
    code="B2.5",
    title="SIKIŞIK DÜZEN VEYA KÖTÜ DÜZENLENMİŞ YERLEŞİM",
    typical_problems=[
        "Dar yerleşim nedeniyle bariyer, izolasyon veya acil kaçış da pratikte kullanılamaz hale gelir",
    ],
    selection_criteria="Dar alan / geçiş yolu kapalı",
    section_ids=["B", "B2"],
)


def test_probe_question_template_tr():
    q = probe_question_for_type("typical_problem", "tr")
    assert "yukarıda özetlenen" in q.lower() or "aşağıda belirtilen" in q.lower()
    assert "bu durum" not in q.lower()


def test_deep_question_splits_context(monkeypatch):
    import agents.hitl_question_service as svc

    monkeypatch.setattr(svc, "_BARSEL_ITEMS", [FIXTURE])
    monkeypatch.setattr(svc, "_BARSEL_BY_CODE", {FIXTURE.code: FIXTURE})

    rows = _build_deep_questions_from_barsel_taxonomy(
        FIXTURE.code,
        why_level=1,
        incident_context="dar alanda çalışma",
        barsel_by_code={FIXTURE.code: FIXTURE},
        barsel_items=[FIXTURE],
    )
    prob_rows = [r for r in rows if r.get("yönler", {}).get("probe_type") == "typical_problem"]
    assert prob_rows
    row = prob_rows[0]
    assert "yukarıda özetlenen" in row["soru"].lower()
    assert "bariyer" in row["probe_context"]
    assert "bariyer" not in row["soru"]


def test_shape_question_exposes_probe_context():
    shaped = _shape_question(
        {
            "id": "x",
            "source": "why_probe_barsel_taxonomy",
            "code": "B2.5",
            "cause_desc": FIXTURE.title,
            "hsg245": "B2.5",
            "soru": probe_question_for_type("typical_problem", "tr"),
            "probe_context": FIXTURE.typical_problems[0],
            "yönler": {"probe_type": "typical_problem"},
        },
        "tr",
    )
    assert shaped["probe_context"] == FIXTURE.typical_problems[0]
    assert shaped["helper_hint"] == FIXTURE.typical_problems[0]
    assert "yukarıda özetlenen" in shaped["question_tr"].lower()
    assert shaped.get("probe_context_label")


def test_probe_dedup_allows_same_template_different_context():
    template = probe_question_for_type("typical_problem", "tr")
    row_a = {
        "code": "D4.3",
        "soru": template,
        "probe_context": "Fiziksel kapasite yetersizdi",
    }
    row_b = {
        "code": "D4.3",
        "soru": template,
        "probe_context": "Standart veya prosedür eksikti",
    }
    seen: set[str] = set()
    assert not _should_skip_probe_row(row_a, seen)
    assert not _should_skip_probe_row(row_b, seen)
    assert _probe_dedup_key(row_a) != _probe_dedup_key(row_b)


def test_build_why_probe_pool_one_relevant_problem_per_code(monkeypatch):
    import agents.hitl_question_service as svc

    multi = BarselTaxonomyItem(
        code="D4.3",
        title="Fiziksel Kapasite",
        typical_problems=[
            "Fiziksel kapasite yetersizdi",
            "Ekipman kapasitesi olay için uygun değildi",
        ],
        selection_criteria="Kapasite yetersiz / ekipman uyumsuz",
        section_ids=["D", "D4"],
    )
    monkeypatch.setattr(svc, "_BARSEL_ITEMS", [multi])
    monkeypatch.setattr(svc, "_BARSEL_BY_CODE", {multi.code: multi})
    monkeypatch.setattr(svc, "_hitl_llm_probe_enabled", lambda: False)
    monkeypatch.setattr(svc, "_hitl_llm_probe_context_enabled", lambda: False)
    monkeypatch.setattr(
        "agents.hitl_question_service.codes_for_why_level",
        lambda *_a, **_k: [multi.code],
    )
    monkeypatch.setattr(
        svc,
        "_hitl_taxonomy_index",
        lambda *_a, **_k: ([multi], {multi.code: multi}),
    )

    pool = build_why_probe_question_pool(
        how_happened="vinç kapasitesi yetersiz kaldı",
        root_cause_initial="",
        immediate_code=multi.code,
        why_level=1,
        output_language="tr",
    )
    prob_rows = [
        r
        for r in pool
        if r.get("yönler", {}).get("probe_type") == "typical_problem"
    ]
    assert len(prob_rows) >= 1
    assert any("kapasite" in r["probe_context"].lower() for r in prob_rows)


def test_build_why_probe_pool_fallback_when_no_typical_problems(monkeypatch):
    import agents.hitl_question_service as svc

    bare = BarselTaxonomyItem(
        code="A4.1",
        title="Yetersiz beceri uygulaması",
        definition=(
            "Kazı tatbikatı sonrası saha davranış doğrulaması prosedürü eksikti veya uygulanmıyordu. "
            "Çalışanlar teorik eğitim almış olsalar da uygulama fırsatı bulamamışlardır."
        ),
        typical_problems=[],
        section_ids=["A", "A4"],
    )
    monkeypatch.setattr(svc, "_BARSEL_ITEMS", [bare])
    monkeypatch.setattr(svc, "_BARSEL_BY_CODE", {bare.code: bare})
    monkeypatch.setattr(svc, "_hitl_llm_probe_enabled", lambda: False)
    monkeypatch.setattr(svc, "_hitl_llm_probe_context_enabled", lambda: False)
    monkeypatch.setattr(
        "agents.hitl_question_service.codes_for_why_level",
        lambda *_a, **_k: [bare.code],
    )
    monkeypatch.setattr(
        svc,
        "_hitl_taxonomy_index",
        lambda *_a, **_k: ([bare], {bare.code: bare}),
    )

    pool = build_why_probe_question_pool(
        how_happened="kazı tatbikatı sonrası saha davranış doğrulaması yapılmadı",
        root_cause_initial="",
        immediate_code=bare.code,
        why_level=1,
        output_language="tr",
    )
    assert len(pool) >= 1
    assert pool[0].get("code") == bare.code


def test_next_why_probe_stops_at_branch_limit(monkeypatch):
    import agents.hitl_question_service as svc

    monkeypatch.setattr(svc, "_hitl_max_probes_per_branch", lambda: 2)
    monkeypatch.setattr(
        svc,
        "_cached_why_probe_pool",
        lambda **_k: [
            {"id": "a", "soru": "q1", "code": "A4.1", "yönler": {}},
            {"id": "b", "soru": "q2", "code": "A4.1", "yönler": {}},
            {"id": "c", "soru": "q3", "code": "A4.1", "yönler": {}},
        ],
    )
    out = svc.next_why_probe_questions(
        how_happened="depo forklift",
        root_cause_initial="",
        answered_ids=["a", "b"],
        immediate_code="A4.1",
        why_level=1,
    )
    assert out["done"] is True
    assert out.get("probe_limit_reached")


def test_shape_question_splits_legacy_embedded_probe():
    legacy = (
        "Bu olayda şu durum geçerli miydi: "
        "Dar yerleşim nedeniyle bariyer kullanılamaz hale gelir?"
    )
    shaped = _shape_question(
        {
            "id": "legacy",
            "source": "why_probe_barsel_taxonomy",
            "code": "B2.5",
            "cause_desc": "SIKIŞIK DÜZEN",
            "hsg245": "B2.5",
            "soru": legacy,
            "yönler": {"probe_type": "typical_problem"},
        },
        "tr",
    )
    assert "bariyer" in shaped["probe_context"]
    assert "bariyer" not in shaped["question_tr"]
    assert "yukarıda özetlenen" in shaped["question_tr"].lower()
