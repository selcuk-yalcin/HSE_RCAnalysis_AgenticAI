"""BARSEL HITL soru üretimi testleri."""

from agents.barsel_taxonomy import (
    BarselTaxonomyItem,
    find_contrast_code,
    pick_typical_problems_for_hitl,
    split_selection_criteria,
)
from agents.hitl_question_service import _build_deep_questions_from_taxonomy, _taxonomy_prompt_context


FIXTURE_ITEMS = [
    BarselTaxonomyItem(
        code="A1.1",
        title="Bireysel Kural İhlali",
        selection_criteria="Kural biliniyordu / Tek birey sapma yaptı",
        typical_problems=[
            "Kural ihlalinin görmezden gelinmiş olması",
            "Eğitim kaydının yeterli sayılması",
        ],
        keywords=["kural biliyordu", "tek başına karar verdi"],
        section_ids=["A", "A1"],
    ),
    BarselTaxonomyItem(
        code="A1.2",
        title="Grup Kural İhlali",
        typical_problems=["Yönetimin ekip ihlallerine müdahale etmemesi"],
        keywords=["hepimiz böyle yapıyoruz"],
        section_ids=["A", "A1"],
    ),
]


def test_split_selection_criteria():
    parts = split_selection_criteria("Birinci koşul / İkinci koşul / Üçüncü")
    assert len(parts) == 2
    assert "Birinci" in parts[0]


def test_pick_typical_problems_rotates_by_why_level():
    incident = "eğitim kaydı var ama uygulama yok kural ihlali"
    p1 = pick_typical_problems_for_hitl(
        FIXTURE_ITEMS[0], incident, why_level=1, max_problems=1, min_relevance=0.0,
    )
    p2 = pick_typical_problems_for_hitl(
        FIXTURE_ITEMS[0], incident, why_level=2, max_problems=1, min_relevance=0.0,
    )
    assert p1 and p2
    assert p1 != p2 or len(FIXTURE_ITEMS[0].typical_problems) == 1


def test_find_contrast_code_same_band():
    contrast = find_contrast_code(FIXTURE_ITEMS[0], FIXTURE_ITEMS)
    assert contrast is not None
    assert contrast.code == "A1.2"


def test_build_deep_questions_barsel_mode(monkeypatch):
    import agents.hitl_question_service as svc

    monkeypatch.setattr(svc, "_BARSEL_ITEMS", FIXTURE_ITEMS)
    monkeypatch.setattr(svc, "_BARSEL_BY_CODE", {i.code: i for i in FIXTURE_ITEMS})
    monkeypatch.setattr(svc, "_USE_BARSEL_HITL", True)

    rows = _build_deep_questions_from_taxonomy(
        "A1.1",
        why_level=1,
        incident_context="çalışan kuralı biliyordu tek başına ihlal etti",
    )
    assert rows
    assert any(
        "aşağıda belirtilen" in r["soru"].lower() or "geçerli miydi" in r["soru"].lower()
        for r in rows
    )
    assert any(r.get("probe_context") for r in rows)
    assert rows[0]["source"] == "why_probe_barsel_taxonomy"


def test_taxonomy_prompt_context_barsel(monkeypatch):
    import agents.hitl_question_service as svc

    monkeypatch.setattr(svc, "_BARSEL_ITEMS", FIXTURE_ITEMS)
    monkeypatch.setattr(svc, "_BARSEL_BY_CODE", {i.code: i for i in FIXTURE_ITEMS})
    monkeypatch.setattr(svc, "_USE_BARSEL_HITL", True)

    ctx = _taxonomy_prompt_context(["A1.1"])
    assert "keywords:" in ctx
    assert "typical_problems:" in ctx
    assert "A1.1" in ctx
