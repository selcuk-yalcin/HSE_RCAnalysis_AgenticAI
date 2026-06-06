"""Mongo-driven Why/HITL flow helpers."""

from agents.barsel_taxonomy import (
    build_definition_based_why_answer,
    codes_for_why_level,
    probe_answer_affirms_fit,
    why_level_target_bands,
)
from agents.hitl_question_service import build_interim_why_question


def test_why_level_target_bands():
    assert why_level_target_bands(1) == ["A", "B"]
    assert why_level_target_bands(2) == ["A", "B"]
    assert why_level_target_bands(3) == ["C"]
    assert why_level_target_bands(4) == ["C"]
    assert why_level_target_bands(5) == ["D"]


def test_codes_for_why_level_includes_immediate_on_early_levels():
    codes = codes_for_why_level(1, "B2.1", "iskele korkuluk eksik", None, max_codes=3)
    assert "B2.1" in codes


def test_probe_answer_affirms_fit():
    assert probe_answer_affirms_fit("Evet")
    assert probe_answer_affirms_fit("yes")
    assert not probe_answer_affirms_fit("Hayır")
    assert not probe_answer_affirms_fit("Bilinmiyor")


def test_build_interim_why1_question():
    q = build_interim_why_question(1, "B2.1", cause_tr="Korkuluk montajı tamamlanmamıştı")
    assert q.startswith("Neden")
    assert "?" in q


def test_critical_factor_and_root_titles_for_d84():
    from agents.barsel_taxonomy import (
        critical_factor_title_for_code,
        enrich_root_cause_from_taxonomy,
        load_barsel_taxonomy_items,
        root_cause_leaf_title_for_code,
    )

    items = load_barsel_taxonomy_items()
    assert items, "barsel taxonomy json should load"
    cf = critical_factor_title_for_code("D8.4")
    assert "SATIN ALMA" in cf.upper()
    assert "MALZEME" in cf.upper()
    assert not cf.upper().startswith("D8.")
    leaf = root_cause_leaf_title_for_code("D8.4")
    assert "depolama" in leaf.lower()
    enriched = enrich_root_cause_from_taxonomy({"code": "D8.4"})
    assert enriched.get("cause_tr") == leaf
    assert enriched.get("critical_factor_title") == cf
    assert len(str(enriched.get("explanation_tr") or "")) > 80


def test_critical_factor_group_titles_from_section_trail():
    from agents.barsel_taxonomy import critical_factor_title_for_code

    assert critical_factor_title_for_code("D8.4") == "SATIN ALMA, MALZEME TAŞIMA VE MALZEME KONTROLÜ"
    assert critical_factor_title_for_code("D9.1") == "Standartlar / Pratikler / Prosedürler (SPP)"
    assert critical_factor_title_for_code("D5.2") == "Mühendislik / Tasarım ve Teknik Sistemler"


def test_resolve_root_code_from_why_chain():
    from agents.barsel_taxonomy import (
        apply_official_taxonomy_titles_to_report_branches,
        resolve_root_cause_code_from_branch,
    )

    raw = {
        "branch_number": 4,
        "root_cause": {"cause_tr": "tasarım girdileri hatalı"},
        "why_chain": [
            {"question": "Neden?", "answer": "Eksik kapak", "code": "B2.1"},
            {"question": "Neden 2?", "answer": "FMEA yapılmadı (D5.2)", "code": "D5.2"},
        ],
    }
    assert resolve_root_cause_code_from_branch(raw) == "D5.2"
    branches = apply_official_taxonomy_titles_to_report_branches(
        [{"branch_number": 4, "branch_title": "KRİTİK FAKTÖR 4 - TEKNİK/EKİPMAN NEDEN"}],
        [raw],
    )
    assert "TEKNİK/EKİPMAN" not in branches[0]["branch_title"]
    assert "Mühendislik / Tasarım" in branches[0]["branch_title"]


def test_d52_official_titles_match_barsel_table():
    from agents.barsel_taxonomy import (
        apply_official_taxonomy_titles_to_report_branches,
        critical_factor_title_for_code,
        root_cause_leaf_title_for_code,
    )

    leaf = root_cause_leaf_title_for_code("D5.2")
    assert "standartlar" in leaf.lower() or "şartname" in leaf.lower()
    assert "Tasarım Girdileri Hatalı" != leaf
    cf = critical_factor_title_for_code("D5.2")
    assert "Mühendislik" in cf or "Tasarım" in cf
    assert not cf.upper().startswith("D5")

    branches = apply_official_taxonomy_titles_to_report_branches(
        [{"branch_number": 4, "root_cause_title": "Tasarım Girdileri Hatalı", "branch_title": "KRİTİK FAKTÖR 4 - TEKNİK/EKİPMAN"}],
        [{"root_cause": {"code": "D5.2"}}],
    )
    assert branches[0]["root_cause_title"] == leaf
    assert "TEKNİK/EKİPMAN" not in branches[0]["branch_title"]
    assert cf in branches[0]["branch_title"]


def test_build_definition_based_why_answer():
    from agents.barsel_taxonomy import BarselTaxonomyItem

    item = BarselTaxonomyItem(
        code="D2.1",
        title="Dikey İletişim Yetersizliği",
        definition="Yönetim ile saha arasında bilgi akışı yetersizdi.",
    )
    ans = build_definition_based_why_answer(item)
    assert "D2.1" in ans
    assert "Dikey" in ans or "yetersiz" in ans.lower()
