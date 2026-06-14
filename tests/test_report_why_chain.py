"""P1.26 — rapor why_chain pin birim testleri."""

from agents.report_why_chain import (
    build_pinned_why_chain,
    build_shared_event_question,
    immediate_cause_report_answer,
    pin_agent_why_chains_to_report,
    validate_report_why_chains,
)


def _sample_raw_branch(branch_no: int = 1) -> dict:
    return {
        "branch_number": branch_no,
        "immediate_cause": {
            "code": "A01",
            "cause_tr": "Keskin talaşa doğrudan temas",
            "standard_title_tr": "Keskin talaşa doğrudan temas",
        },
        "why_chain": [
            {"level": 1, "question_tr": "ignored", "answer_tr": "ignored"},
            {
                "level": 2,
                "question_tr": "Neden keskin talaşa temas oldu?",
                "answer_tr": "Koruyucu eldiven kullanılmadı",
            },
            {
                "level": 3,
                "question_tr": "Neden eldiven kullanılmadı?",
                "answer_tr": "Eldiven stoğu tükendi",
            },
            {
                "level": 4,
                "question_tr": "Neden stok tükendi?",
                "answer_tr": "Tedarik planlaması yapılmadı",
            },
            {
                "level": 5,
                "question_tr": "Neden planlama yapılmadı?",
                "answer_tr": "KKD yönetim prosedürü uygulanmadı",
            },
        ],
        "root_cause": {
            "code": "D12",
            "cause_tr": "KKD yönetim prosedürü uygulanmadı",
            "explanation_tr": "Organizasyonel prosedür eksikliği",
        },
    }


def test_build_shared_event_question():
    incident = "Konveyör bandında yatak arızası nedeniyle duruş yaşanmıştır."
    q = build_shared_event_question(incident)
    assert q.startswith("Neden ")
    assert "meydana geldi?" in q


def test_immediate_cause_report_answer_from_taxonomy():
    ans = immediate_cause_report_answer(
        {"code": "A01", "cause_tr": "Keskin talaşa doğrudan temas"}
    )
    assert "Keskin talaşa" in ans
    assert "A01" not in ans


def test_build_pinned_why_chain_five_steps_shared_w1():
    incident = "Operatör parça düşmesi riski altında çalıştı."
    shared_q = build_shared_event_question(incident)
    chain, warnings = build_pinned_why_chain(_sample_raw_branch(), shared_q)
    assert len(chain) == 5
    assert chain[0]["number"] == 1
    assert chain[0]["question"] == shared_q
    assert "Keskin talaşa" in chain[0]["answer"]
    assert chain[1]["question"].startswith("Neden ")
    assert not warnings


def test_pin_overwrites_llm_why_chain():
    incident = "Parça düşme riski oluştu."
    shared_q = build_shared_event_question(incident)
    raw_data = {
        "part3_rca": {
            "incident_summary": incident,
            "analysis_branches": [_sample_raw_branch(1), _sample_raw_branch(2)],
        }
    }
    llm_content = {
        "branches": [
            {
                "branch_number": 1,
                "why_chain": [
                    {"number": 1, "question": "LLM dal 1 sorusu", "answer": "LLM uzun anlatı"},
                    {"number": 2, "question": "q2", "answer": "a2"},
                ],
            },
            {
                "branch_number": 2,
                "why_chain": [
                    {"number": 1, "question": "Farklı LLM sorusu", "answer": "Başka cevap"},
                ],
            },
        ]
    }
    pinned = pin_agent_why_chains_to_report(llm_content, raw_data)
    for br in pinned["branches"]:
        assert len(br["why_chain"]) == 5
        assert br["why_chain"][0]["question"] == shared_q
        assert "LLM" not in br["why_chain"][0]["question"]
        assert "Keskin talaşa" in br["why_chain"][0]["answer"]


def test_validate_report_why_chains_detects_mismatch():
    issues = validate_report_why_chains(
        [
            {"branch_number": 1, "why_chain": [{"number": 1, "question": "A", "answer": "x"}]},
            {"branch_number": 2, "why_chain": [{"number": 1, "question": "B", "answer": "y"}]},
        ]
    )
    assert any("5 olmalı" in i for i in issues)
    assert any("aynı değil" in i for i in issues)
