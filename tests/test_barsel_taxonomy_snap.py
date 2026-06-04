"""BARSEL taxonomy snap + category prompt tests."""

from agents.barsel_taxonomy import (
    get_barsel_category_prompt,
    get_incident_taxonomy_prompt,
    get_taxonomy_category_text,
    snap_immediate_cause_to_barsel,
    snap_to_barsel_taxonomy,
)


def test_barsel_category_prompt_has_ab_codes():
    text = get_barsel_category_prompt("A")
    assert "BARSEL" in text
    assert "A1.1" in text
    assert "Bireysel" in text or "Kural" in text


def test_cd_prompt_includes_root_bands():
    text = get_barsel_category_prompt("CD")
    assert "C1." in text or "C band" in text
    assert "D1." in text or "D band" in text


def test_snap_root_cause_to_barsel_title():
    snapped = snap_to_barsel_taxonomy(
        "D3.1",
        "yönetim gözetimi yetersizdi",
        "5-Why zinciri açıklaması",
        family="cd",
    )
    assert snapped is not None
    assert snapped["code"].startswith("D")
    assert snapped["category_type"] == "ORGANİZASYONEL"
    assert snapped["cause_tr"]


def test_snap_immediate_cause_ab():
    raw = {
        "code": "A1.2",
        "cause_tr": "ekipçe toplu kural ihlali",
        "category_type": "A",
        "standard_title_tr": "",
        "evidence_tr": "test",
    }
    out = snap_immediate_cause_to_barsel(raw)
    assert out["code"] == "A1.2"
    assert "Grup" in out["standard_title_tr"] or "Takım" in out["standard_title_tr"]


def test_get_incident_taxonomy_prompt_uses_rag(monkeypatch):
    from rag_pipeline.retrieval.barsel_taxonomy_retriever import BarselTaxonomyRetriever
    from tests.test_barsel_taxonomy_retrieval import FIXTURE_DOCS

    monkeypatch.setenv("ROOTCAUSE_TAXONOMY_MODE", "rag")
    r = BarselTaxonomyRetriever(documents=FIXTURE_DOCS)
    text = get_incident_taxonomy_prompt(
        "A",
        "ekipçe toplu kural ihlali hepimiz böyle yapıyoruz",
        r,
    )
    assert "BARSEL RAG" in text
    assert "A1.2" in text


def test_get_incident_taxonomy_prompt_static_fallback(monkeypatch):
    monkeypatch.setenv("ROOTCAUSE_TAXONOMY_MODE", "static")
    text = get_incident_taxonomy_prompt("A", "test", retriever=None)
    assert "statik" in text.lower() or "BARSEL" in text
