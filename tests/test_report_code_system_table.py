"""Rapor 3.2 BARSEL kod tablosu."""

from agents.skillbased_docx_agent import _default_barsel_code_system, _normalize_analysis_method
from shared.report_i18n import set_report_lang


def test_default_code_system_abcd_labels_tr():
    set_report_lang("tr")
    rows = _default_barsel_code_system("tr")
    by_code = {r["code"]: r["category"] for r in rows}
    assert by_code == {
        "A": "Davranış",
        "B": "Koşullar",
        "C": "Kişisel",
        "D": "Organizasyonel",
    }


def test_normalize_analysis_method_fixes_wrong_categories():
    set_report_lang("tr")
    method = _normalize_analysis_method(
        {
            "code_system": [
                {"code": "A", "category": "İnsan Faktörü", "description": "x"},
                {"code": "B", "category": "Organizasyonel Faktör", "description": "y"},
            ]
        }
    )
    by_code = {r["code"]: r["category"] for r in method["code_system"]}
    assert by_code["A"] == "Davranış"
    assert by_code["B"] == "Koşullar"
    assert by_code["C"] == "Kişisel"
    assert by_code["D"] == "Organizasyonel"
