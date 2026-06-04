"""BARSEL iki aşamalı retriever testleri (Mongo gerekmez)."""

from rag_pipeline.retrieval.barsel_taxonomy_retriever import BarselTaxonomyRetriever


FIXTURE_DOCS = [
    {
        "code": "A1.1",
        "cause_type": "immediate_cause",
        "section_ids": ["A", "A1"],
        "keywords": {"tr": ["bilerek ihlal", "kural biliyordu", "kasıtlı sapma"]},
        "content": {
            "tr": {
                "title": "Bireysel Kural / Prosedür İhlali",
                "definition": "Tek çalışanın bilerek kural ihlali.",
                "typical_problems": [
                    "Kural ihlalinin görmezden gelinmiş olması",
                ],
            }
        },
        "exclusion_conditions": [],
    },
    {
        "code": "A1.2",
        "cause_type": "immediate_cause",
        "section_ids": ["A", "A1"],
        "keywords": {"tr": ["toplu kural ihlali", "ekipçe kural dışı davranış"]},
        "content": {
            "tr": {
                "title": "Grup / Takım Kural İhlali",
                "definition": "Birden fazla kişinin kolektif kural ihlali.",
                "typical_problems": ["Yönetimin ekip ihlallerine müdahale etmemesi"],
            }
        },
        "exclusion_conditions": [],
    },
    {
        "code": "B2.1",
        "cause_type": "root_cause",
        "section_ids": ["B", "B2"],
        "keywords": {"tr": ["arızalı ekipman", "bozuk alet"]},
        "content": {
            "tr": {
                "title": "Arızalı Ekipman",
                "definition": "Ekipman arızası koşul nedeni.",
                "typical_problems": ["Bakım kaydı eksik"],
            }
        },
        "exclusion_conditions": [],
    },
]


def test_keyword_filter_prefers_group_violation():
    r = BarselTaxonomyRetriever(documents=FIXTURE_DOCS)
    hits = r.retrieve_hits(
        "ekipçe toplu kural ihlali yaptık hepimiz böyle yapıyoruz",
        k=2,
        keyword_pool=10,
    )
    assert hits
    assert hits[0].code == "A1.2"


def test_keyword_filter_individual_violation():
    r = BarselTaxonomyRetriever(documents=FIXTURE_DOCS)
    hits = r.retrieve_hits(
        "çalışan bilerek kasıtlı sapma ile kuralı biliyordu yine de ihlal etti",
        k=1,
    )
    assert hits[0].code == "A1.1"


def test_band_filter():
    r = BarselTaxonomyRetriever(documents=FIXTURE_DOCS)
    hits = r.retrieve_hits("arızalı ekipman kullanımı", k=3, band="B")
    assert all(h.code.startswith("B") for h in hits)


def test_retrieve_dict_shape():
    r = BarselTaxonomyRetriever(documents=FIXTURE_DOCS)
    results = r.retrieve("kural ihlali bilerek", k=2)
    assert results
    assert "similarityScore" in results[0]
    assert "keywordScore" in results[0]
    assert "semanticScore" in results[0]
