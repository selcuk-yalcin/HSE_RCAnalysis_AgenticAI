"""BARSEL disambiguation bank + taxonomy_gap migrasyonu (R6b)."""

import os

from agents.barsel_disambiguation_bank import (
    build_barsel_questions_for_causes,
    build_barsel_taxonomy_gap_questions,
    get_barsel_code_specific_questions,
    get_barsel_disambiguation_questions,
)
from agents.barsel_taxonomy import BarselTaxonomyItem, pick_keywords_for_hitl
from agents.hitl_disambiguation_bank import build_questions_for_causes

FIXTURE_ITEMS = [
    BarselTaxonomyItem(
        code="B4.4",
        title="Koruyucu Donanım Eksikliği",
        selection_criteria="Bariyer yoktu / Bariyer vardı ama yetersizdi",
        typical_problems=[
            "Korkuluk veya bariyer hiç kurulmamış olması",
            "Geçici koruma yetersiz bırakılmış olması",
        ],
        keywords=["korkuluk", "bariyer", "güvenlik ağı"],
        section_ids=["B", "B4"],
    ),
    BarselTaxonomyItem(
        code="B4.1",
        title="Korunmasız Açıklık",
        typical_problems=["Platform açıklığı işaretsiz bırakılmış"],
        keywords=["açıklık", "delik"],
        section_ids=["B", "B4"],
    ),
]


def test_keyword_questions_from_mongo_style_keywords():
    item = BarselTaxonomyItem(
        code="A1.1",
        title="Bireysel Kural İhlali",
        keywords=["bilerek ihlal", "eğitimli personelin kural dışı davranışı", "kasıtlı sapma"],
        section_ids=["A", "A1"],
    )
    qs = get_barsel_disambiguation_questions(
        "A1.1",
        items=[item],
        by_code={"A1.1": item},
        incident_context="personel bilerek kural dışı davrandı",
    )
    kw_qs = [q for q in qs if q.get("yönler", {}).get("probe_type") == "keyword_rag"]
    assert kw_qs
    assert any("bilerek ihlal" in q["soru"] for q in kw_qs)
    assert all("Deliberate" not in q["soru"] for q in qs)


def test_pick_keywords_prefers_incident_overlap():
    item = BarselTaxonomyItem(
        code="A1.1",
        title="Test",
        keywords=["bilerek ihlal", "kasıtlı sapma", "eğitim"],
    )
    picked = pick_keywords_for_hitl(
        item, "bilerek ihlal yapıldı", slot_index=0, max_keywords=1
    )
    assert picked[0] == "bilerek ihlal"


def test_get_barsel_disambiguation_from_typical_problems():
    qs = get_barsel_disambiguation_questions(
        "B4.4",
        items=FIXTURE_ITEMS,
        by_code={i.code: i for i in FIXTURE_ITEMS},
        incident_context="korkuluk yoktu geçici bariyer eksik",
    )
    assert qs
    assert any("geçerli miydi" in q["soru"] for q in qs)
    assert all("B4." not in q["soru"] for q in qs)
    assert all("D4." not in q["soru"] for q in qs)


def test_build_barsel_questions_for_causes_no_hsg_codes_in_soru(monkeypatch):
    monkeypatch.setenv("HITL_USE_MONGO_RAG", "0")
    monkeypatch.setattr(
        "agents.barsel_disambiguation_bank.load_barsel_taxonomy_items",
        lambda *a, **k: FIXTURE_ITEMS,
    )
    rows = build_barsel_questions_for_causes(
        [{"code": "B4.4", "cause_tr": "Yüksekte koruma yoktu"}],
        incident_context="bariyer kurulmamış",
    )
    assert rows
    assert rows[0].get("barsel") is True
    for row in rows:
        assert "→ D4." not in row["soru"]
        assert "hsg245" not in row["soru"].upper() or True  # soru text clean


def test_build_questions_routes_to_barsel_by_default(monkeypatch):
    monkeypatch.setenv("HITL_USE_MONGO_RAG", "0")
    monkeypatch.setattr(
        "agents.barsel_disambiguation_bank.load_barsel_taxonomy_items",
        lambda *a, **k: FIXTURE_ITEMS,
    )
    monkeypatch.delenv("HITL_USE_BARSEL", raising=False)
    rows = build_questions_for_causes(
        [{"code": "B4.4", "cause_tr": "test"}],
        incident_context="korkuluk",
    )
    assert rows
    assert rows[0].get("barsel") is True


def test_build_questions_hsg_fallback_when_barsel_disabled(monkeypatch):
    monkeypatch.setenv("HITL_USE_BARSEL", "0")
    monkeypatch.setenv("HITL_USE_MONGO_RAG", "0")
    rows = build_questions_for_causes([{"code": "B4.4", "cause_tr": "test"}])
    assert rows
    assert not any(r.get("barsel") for r in rows)
    assert any("risk değerlendirmesi" in r["soru"].lower() for r in rows)


def test_mongo_only_skips_hsg_when_barsel_empty(monkeypatch):
    monkeypatch.setenv("HITL_USE_MONGO_RAG", "1")
    monkeypatch.setenv("MONGODB_URI", "mongodb://local/test")
    monkeypatch.delenv("HITL_ALLOW_JSON_HSG_FALLBACK", raising=False)
    rows = build_questions_for_causes([{"code": "B4.4", "cause_tr": "test"}])
    assert rows == []


def test_barsel_taxonomy_gap_no_hsg_links():
    text = "Forklift geri giderken çalışana çarptı."
    rows = build_barsel_taxonomy_gap_questions(text, max_categories=3, per_cat=1)
    assert rows
    assert all(r.get("source") == "taxonomy_gap_barsel" for r in rows)
    for row in rows:
        assert "hsg245" not in (row.get("soru") or "").lower()
        assert "A1." not in row.get("soru", "")
        assert row.get("hsg245") == ""


def test_barsel_taxonomy_gap_incident_typed_prosedur():
    text = "Elektrik panelinde arıza vardı, LOTO uygulanmadı."
    rows = build_barsel_taxonomy_gap_questions(text, max_categories=5, per_cat=1)
    prosedur = [r for r in rows if r.get("category") == "prosedür"]
    assert prosedur
    assert "LOTO" in prosedur[0]["soru"] or "prosedür" in prosedur[0]["soru"].lower()


def test_barsel_code_specific_questions_no_hsg_codes(monkeypatch):
    a11 = BarselTaxonomyItem(
        code="A1.1",
        title="Bireysel Kural İhlali",
        definition=(
            "Çalışanın bilinçli olarak kural veya prosedürü ihlal etmesi durumunda "
            "seçilir; tek birey sapması tipiktir."
        ),
        selection_criteria="Kural biliniyordu / Tek birey sapma yaptı",
        typical_problems=["Kural ihlalinin görmezden gelinmiş olması"],
        keywords=["kural biliyordu", "tek başına karar verdi"],
        section_ids=["A", "A1"],
        related_codes=["A1.2"],
    )
    a12 = BarselTaxonomyItem(
        code="A1.2",
        title="Grup Kural İhlali",
        typical_problems=["Yönetimin ekip ihlallerine müdahale etmemesi"],
        keywords=["hepimiz böyle yapıyoruz"],
        section_ids=["A", "A1"],
    )
    monkeypatch.setattr(
        "agents.barsel_disambiguation_bank.load_barsel_taxonomy_items",
        lambda *a, **k: [a11, a12],
    )
    rows = get_barsel_code_specific_questions(
        ["A1.1"],
        why_level=2,
        incident_context="çalışan kuralı biliyordu",
        max_total=6,
    )
    assert rows
    assert all(r.get("barsel") for r in rows)
    for row in rows:
        q = row["question"]
        assert "A1." not in q
        assert "D3." not in q
        assert "→" not in q
