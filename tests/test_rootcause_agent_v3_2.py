"""V3.2 trainset W1 birim testleri (DSPy/LLM çağrısı yok)."""

import importlib.util
import sys
from pathlib import Path

# Paket __init__ lazy; kalite modülünü doğrudan yükle
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

build_trainset_why1_question_heuristic = _mod.build_trainset_why1_question_heuristic
immediate_cause_ab_answer = _mod.immediate_cause_ab_answer


KIMYA_INCIDENT = (
    "Solvent transfer hattında flanş bağlantısından küçük sızıntı tespit edildi; "
    "operatör bölgede KKD olmadan kısa süre kaldı ve baş dönmesi şikayetiyle "
    "sağlık birimine yönlendirildi."
)


def test_trainset_why1_question_kimya_heuristic():
    q = build_trainset_why1_question_heuristic(KIMYA_INCIDENT)
    assert q.startswith("Neden ")
    assert "?" in q
    assert "solvent" in q.lower() or "maruz" in q.lower() or "kimyasal" in q.lower()


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


def test_v3_2_status_inactive():
    try:
        from agents.v3_2 import check_v3_2_status
    except Exception as exc:  # noqa: BLE001 — dspy sandbox
        import pytest

        pytest.skip(f"dspy/v3_1 unavailable: {exc}")

    st = check_v3_2_status()
    assert st["version"] == "3.2"
    assert st["active_in_production"] is False
