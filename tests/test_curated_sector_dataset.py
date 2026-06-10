"""Curated sector 5-Why dataset schema and split tests."""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "agents" / "synetic_data_preperation"


def _load_jsonl(name: str):
    path = DATA_DIR / name
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


@pytest.fixture(scope="module")
def metadata():
    return json.loads((DATA_DIR / "hse_dataset_metadata.json").read_text(encoding="utf-8"))


def test_dataset_files_exist():
    for name in ("hse_5why_train.jsonl", "hse_5why_dev.jsonl", "hse_5why_test.jsonl"):
        assert (DATA_DIR / name).exists()


def test_split_sizes(metadata):
    train = _load_jsonl("hse_5why_train.jsonl")
    dev = _load_jsonl("hse_5why_dev.jsonl")
    test = _load_jsonl("hse_5why_test.jsonl")
    assert metadata["splits"]["train"] == len(train)
    assert metadata["splits"]["dev"] == len(dev)
    assert metadata["splits"]["test"] == len(test)
    assert len(train) + len(dev) + len(test) == metadata["n_total"]
    assert metadata["n_total"] >= 30


def test_positive_negative_balance(metadata):
    all_rows = (
        _load_jsonl("hse_5why_train.jsonl")
        + _load_jsonl("hse_5why_dev.jsonl")
        + _load_jsonl("hse_5why_test.jsonl")
    )
    pos = [r for r in all_rows if not r.get("is_negative_example")]
    neg = [r for r in all_rows if r.get("is_negative_example")]
    assert len(pos) == metadata["n_positive"]
    assert len(neg) == metadata["n_negative"]
    assert len(neg) >= 10
    assert len(pos) >= 15


def test_each_example_has_five_whys():
    all_rows = (
        _load_jsonl("hse_5why_train.jsonl")
        + _load_jsonl("hse_5why_dev.jsonl")
        + _load_jsonl("hse_5why_test.jsonl")
    )
    for row in all_rows:
        chain = row.get("why_chain") or []
        assert len(chain) == 5, row.get("example_id")
        assert chain[-1].get("is_root_cause") is True
        assert chain[0].get("is_root_cause") is False


def test_negative_examples_have_reason():
    all_rows = (
        _load_jsonl("hse_5why_train.jsonl")
        + _load_jsonl("hse_5why_dev.jsonl")
        + _load_jsonl("hse_5why_test.jsonl")
    )
    for row in all_rows:
        if row.get("is_negative_example"):
            assert row.get("negative_reason"), row.get("example_id")


def test_user_curated_good_examples_present():
    train = _load_jsonl("hse_5why_train.jsonl")
    dev = _load_jsonl("hse_5why_dev.jsonl")
    test = _load_jsonl("hse_5why_test.jsonl")
    ids = {r.get("example_id") for r in train + dev + test}
    expected = {
        "good_mfg_cnc_downtime",
        "good_saas_payment_outage",
        "good_healthcare_med_errors",
        "good_edtech_completion",
    }
    assert expected.issubset(ids)


def test_barsel_codes_on_hse_examples():
    all_rows = (
        _load_jsonl("hse_5why_train.jsonl")
        + _load_jsonl("hse_5why_dev.jsonl")
        + _load_jsonl("hse_5why_test.jsonl")
    )
    with_codes = [r for r in all_rows if r.get("barsel_codes")]
    assert len(with_codes) >= 20
