from agents.training.barsel_eval_metrics import (
    aggregate_retrieval_report,
    any_hit_at_k,
    band_purity,
    recall_at_k,
)


def test_recall_at_k_partial():
    assert recall_at_k(["A1.2", "B4.4"], ["A1.2", "A1.1"], k=2) == 0.5


def test_any_hit():
    assert any_hit_at_k(["D3.1", "D1.1"], ["D3.1"], k=2)


def test_band_purity():
    assert band_purity(["A1.1", "A1.2", "B1.1"], "A", k=2) == 1.0


def test_aggregate():
    rep = aggregate_retrieval_report(
        [
            {"immediate_recall_at_k": 1.0, "root_recall_at_k": 0.5, "immediate_any_hit": True, "root_any_hit": True, "immediate_band_purity": 1.0, "root_band_purity": 0.8},
            {"immediate_recall_at_k": 0.0, "root_recall_at_k": 0.0, "immediate_any_hit": False, "root_any_hit": False, "immediate_band_purity": 0.5, "root_band_purity": 0.5},
        ]
    )
    assert rep["n"] == 2
    assert rep["immediate_any_hit_rate"] == 0.5
