"""V3.2 rapor why_chain pin birim testleri."""

from agents.v3_2.report_why_chain_v3_2 import pin_agent_why_chains_to_report_v32

KIMYA_INCIDENT = (
    "Solvent transfer hattında flanş bağlantısından küçük sızıntı tespit edildi; "
    "operatör bölgede KKD olmadan kısa süre kaldı."
)


def test_pin_overwrites_llm_why_chain_v32():
    raw_data = {
        "part3_rca": {
            "incident_summary": KIMYA_INCIDENT,
            "analysis_branches": [
                {
                    "branch_number": 1,
                    "immediate_cause": {
                        "code": "B2.1",
                        "cause_tr": "Kimyasal maruziyet",
                        "evidence_tr": "Flanş bağlantısından sürekli küçük sızıntı vardı.",
                    },
                    "why_chain": [
                        {"level": 1, "question_tr": "ignored", "answer_tr": "ignored"},
                        {"level": 2, "question_tr": "Neden flanştan sızıntı devam ediyordu?", "answer_tr": "Conta yaşlı"},
                        {"level": 3, "question_tr": "Neden tork yapılmadı?", "answer_tr": "Liste yok"},
                        {"level": 4, "question_tr": "Neden listede yok?", "answer_tr": "RE düşük öncelik"},
                        {"level": 5, "question_tr": "Neden PM yok?", "answer_tr": "Köprü süreç yok"},
                    ],
                }
            ],
        }
    }
    llm = {
        "branches": [
            {
                "branch_number": 1,
                "why_chain": [
                    {"number": 1, "question": "LLM uzun soru", "answer": "LLM uzun cevap"},
                ],
            }
        ]
    }
    pinned = pin_agent_why_chains_to_report_v32(llm, raw_data)
    wc = pinned["branches"][0]["why_chain"]
    assert len(wc) == 5
    assert "solvent" in wc[0]["question"].lower() or "maruz" in wc[0]["question"].lower()
    assert "Flanş" in wc[0]["answer"]
    assert "LLM" not in wc[0]["question"]
    assert wc[1]["question"].startswith("Neden flanş")
