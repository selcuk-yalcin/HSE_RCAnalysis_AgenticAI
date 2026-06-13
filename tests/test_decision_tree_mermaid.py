"""Decision tree — klasik 5-Why ilk soru."""

from agents.decision_tree_mermaid import DecisionTreeGenerator


def test_first_why_question_from_event_not_injury():
    gen = DecisionTreeGenerator()
    incident = (
        "3. katta mobil iskele üzerinde boya işi yapılırken platform dengesini kaybetti."
    )
    q = gen._build_first_why_question(incident)
    assert q.startswith("Neden ")
    assert "yaralandı" not in q.lower()


def test_mermaid_graph_uses_event_question_for_why1():
    gen = DecisionTreeGenerator()
    branches = [
        {
            "branch_number": 1,
            "immediate_cause": {"cause_tr": "Tekerlek frenleri devre dışıydı"},
            "why_chain": [
                {
                    "level": 1,
                    "question_tr": "ignored",
                    "answer_tr": "ignored",
                },
                {
                    "level": 2,
                    "question_tr": "Neden tekerlek frenleri devre dışıydı?",
                    "answer_tr": "Kontrol yapılmamıştı.",
                },
            ],
            "root_cause": {"code": "D3.2", "cause_tr": "Bakım sistemi eksikliği"},
        }
    ]
    incident = "Mobil iskele platformu çöktü."
    mermaid = gen._generate_mermaid_graph(branches, incident)
    assert "yaralandı" not in mermaid.lower()
    assert "Neden" in mermaid
    assert "Tekerlek frenleri" in mermaid
