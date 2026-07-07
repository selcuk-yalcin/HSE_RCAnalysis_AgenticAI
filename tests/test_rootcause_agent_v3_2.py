"""V3.2 olay-zarar W1 birim testleri (DSPy/LLM çağrısı yok)."""

import importlib.util
import sys
from pathlib import Path

_quality_path = (
    Path(__file__).resolve().parent.parent
    / "agents"
    / "v3_2"
    / "why_chain_quality_v3_2.py"
)
_spec = importlib.util.spec_from_file_location(
    "why_chain_quality_v3_2_test", _quality_path
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

build_incident_harm_why1_question_heuristic = _mod.build_incident_harm_why1_question_heuristic
build_trainset_why1_question_heuristic = _mod.build_trainset_why1_question_heuristic
immediate_cause_ab_answer = _mod.immediate_cause_ab_answer

KIMYA_INCIDENT = (
    "Solvent transfer hattında flanş bağlantısından küçük sızıntı tespit edildi; "
    "operatör bölgede KKD olmadan kısa süre kaldı ve baş dönmesi şikayetiyle "
    "sağlık birimine yönlendirildi."
)

HASAN_INCIDENT = (
    "İskele montaj işçisi Hasan Yıldız (32) yaklaşık 6 metre yükseklikteki iskeleden "
    "düşerek zemine çakıldı. Emniyet kemeri takılmamıştı."
)

V31_BAD_WHY1 = (
    "Neden İskele montaj işçisi Hasan Yıldız (32) yaklaşık 6 metre yükseklikteki "
    "iskeleden düşerek zemine çakıldı meydana geldi?"
)


def test_hasan_fall_why1():
    q = build_incident_harm_why1_question_heuristic(HASAN_INCIDENT)
    assert "Hasan" in q
    assert "6" in q
    assert "düş" in q.lower() or "yaraland" in q.lower()
    assert "meydana geldi" not in q.lower()
    assert "montaj" not in q.lower() or q.lower().index("neden") < q.lower().find("montaj")


def test_rejects_v31_meydana_geldi_pattern():
    from agents.v3_2.why_chain_quality_v3_2 import is_invalid_why1_question

    assert is_invalid_why1_question(V31_BAD_WHY1) is True
    assert is_invalid_why1_question(
        "Neden Hasan Yıldız 6 metre yükseklikten düşerek ağır yaralandı?"
    ) is False


GARCIA_INCIDENT = (
    "29.06.2026 tarihinde EAK (Eğik Askılı Köprü) bölgesinde, VSL firması tarafından "
    "Batı Pilon bölgesinde segment strand halat montaj faaliyeti yürütülmekteydi. "
    "Montaj sırasında vinç zincir kancasının mandalı açıldı ve Garcia isimli personel "
    "3,8 metre yükseklikten düşerek ağır yaralandı."
)


def test_trainset_why1_question_kimya_heuristic():
    q = build_trainset_why1_question_heuristic(KIMYA_INCIDENT)
    assert q.startswith("Neden ")
    assert "?" in q
    assert "solvent" in q.lower() or "maruz" in q.lower() or "kimyasal" in q.lower()
    assert "montaj" not in q.lower()


def test_garcia_fall_why1_not_activity():
    """V3.1 hatası: montaj cümlesi yerine yaralanma sorusu."""
    q = build_incident_harm_why1_question_heuristic(GARCIA_INCIDENT)
    assert q.startswith("Neden ")
    assert "Garcia" in q
    assert "düş" in q.lower() or "yaraland" in q.lower()
    assert "3.8" in q or "3,8" in q
    assert "montaj" not in q.lower()
    assert "strand halat" not in q.lower()
    assert "meydana geldi" not in q.lower()


def test_immediate_cause_ab_answer_prefers_evidence():
    ans, code = immediate_cause_ab_answer(
        {
            "code": "B2.1",
            "cause_tr": "Kimyasal maruziyet",
            "standard_title_tr": "Kimyasal maruziyet",
            "evidence_tr": (
                "Flanş bağlantısından sürekli küçük sızıntı vardı ve bölgede "
                "yeterli havalandırma sağlanmamıştı."
            ),
        }
    )
    assert "Flanş" in ans
    assert code == "B2.1"


def test_immediate_cause_ab_answer_falls_back_to_cause_tr():
    ans, code = immediate_cause_ab_answer(
        {"code": "A1.2", "cause_tr": "KKD kullanılmadı.", "evidence_tr": ""}
    )
    assert "KKD" in ans
    assert code == "A1.2"


def test_ptw_branch_ab_answer():
    ans, code = immediate_cause_ab_answer(
        {
            "code": "A3.1",
            "cause_tr": "Deforme kanca kullanımı",
            "evidence_tr": (
                "Vinç zincir kancasının mandalı açıldı; kancada 4-10 mm deformasyon "
                "tespit edilmiş olmasına rağmen ekipman servis dışı bırakılmamıştı."
            ),
        }
    )
    assert "kanca" in ans.lower() or "mandal" in ans.lower()
    assert code == "A3.1"


def test_v3_2_status_active_by_default():
    try:
        from agents.v3_2 import check_v3_2_status
        from agents.root_cause_factory import resolve_root_cause_agent_version
    except Exception as exc:  # noqa: BLE001 — dspy sandbox
        import pytest

        pytest.skip(f"dspy/v3_1 unavailable: {exc}")

    st = check_v3_2_status()
    assert st["version"] == "3.2"
    if resolve_root_cause_agent_version() == "3.2":
        assert st["active_in_production"] is True
    assert "v31_bug" in st
