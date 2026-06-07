"""P1.23-G5: chain_audit_store kayıt üretimi birim testi."""

from shared.chain_audit_store import build_chain_audit_records


def _part3_fixture() -> dict:
    return {
        "_v2_raw": {
            "analysis_branches": [
                {
                    "branch_number": 1,
                    "root_cause": {
                        "code": "D4.1",
                        "cause_tr": "Vana elle zorlanarak açıldı",
                        "standard_title_tr": "Risk değerlendirme süreci eksikliği",
                        "snap_audit_jaccard": 0.03,
                        "snap_overridden": True,
                        "snap_rejected": True,
                    },
                    "chain_quality": 0.62,
                    "why_chain": [
                        {"level": 5, "answer_tr": "Vana elle aşırı zorlanarak açıldı."},
                    ],
                },
                {
                    "branch_number": 2,
                    "root_cause": {
                        "code": "C2.1",
                        "cause_tr": "Eğitim uygulaması yetersizdi",
                        "standard_title_tr": "Yetersiz eğitim",
                        "snap_audit_jaccard": 0.41,
                        "snap_overridden": False,
                        "snap_rejected": False,
                    },
                    "chain_quality": 0.88,
                    "why_chain": [
                        {"number": 5, "answer": "Eğitim periyodu uygulanmadı."},
                    ],
                },
            ]
        }
    }


def test_build_chain_audit_records_extracts_fields():
    records = build_chain_audit_records(
        tenant_id="t1",
        incident_id="inc1",
        part3=_part3_fixture(),
        analysis_model_preset="balanced",
    )
    assert len(records) == 2
    r0 = records[0]
    assert r0["tenant_id"] == "t1"
    assert r0["incident_id"] == "inc1"
    assert r0["root_code"] == "D4.1"
    assert r0["snap_overridden"] is True
    assert r0["snap_audit_jaccard"] == 0.03
    assert r0["chain_quality"] == 0.62
    assert "Vana elle" in r0["why5_answer"]
    assert r0["analysis_model_preset"] == "balanced"
    r1 = records[1]
    assert r1["root_code"] == "C2.1"
    assert r1["snap_overridden"] is False
    assert "Eğitim periyodu" in r1["why5_answer"]


def test_build_chain_audit_records_handles_plain_part3():
    # _v2_raw yoksa doğrudan part3 üzerinden çalışmalı.
    part3 = _part3_fixture()["_v2_raw"]
    records = build_chain_audit_records(tenant_id="t1", incident_id="inc1", part3=part3)
    assert len(records) == 2
