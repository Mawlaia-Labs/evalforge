import json
import csv
import tempfile
from pathlib import Path
from evalforge.datasets import from_json, from_jsonl, from_csv, load


def test_from_json_list(tmp_path):
    data = [
        {"input": "What is 2+2?", "expected": "4"},
        {"input": "Capital of France?", "expected": "Paris", "tags": ["geo"]},
    ]
    p = tmp_path / "evals.json"
    p.write_text(json.dumps(data))
    ds = from_json(p)
    assert len(ds) == 2
    assert ds.cases[1].expected == "Paris"
    assert "geo" in ds.cases[1].tags


def test_from_json_named(tmp_path):
    data = {"name": "my-evals", "cases": [{"input": "hello", "expected": "hi"}]}
    p    = tmp_path / "x.json"
    p.write_text(json.dumps(data))
    ds = from_json(p)
    assert ds.name == "my-evals"


def test_from_jsonl(tmp_path):
    lines = [
        '{"input": "q1", "expected": "a1"}',
        '{"input": "q2", "expected": "a2"}',
    ]
    p = tmp_path / "evals.jsonl"
    p.write_text("\n".join(lines))
    ds = from_jsonl(p)
    assert len(ds) == 2
    assert ds.cases[0].input == "q1"


def test_from_csv(tmp_path):
    p = tmp_path / "evals.csv"
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["input", "expected"])
        w.writeheader()
        w.writerow({"input": "2+2", "expected": "4"})
        w.writerow({"input": "3+3", "expected": "6"})
    ds = from_csv(p)
    assert len(ds) == 2
    assert ds.cases[1].expected == "6"


def test_load_dispatches_by_extension(tmp_path):
    p = tmp_path / "evals.jsonl"
    p.write_text('{"input": "hi", "expected": "hello"}\n')
    ds = load(p)
    assert len(ds) == 1


def test_load_unsupported_format(tmp_path):
    p = tmp_path / "evals.txt"
    p.write_text("not supported")
    try:
        load(p)
        assert False, "should have raised"
    except ValueError as e:
        assert ".txt" in str(e)


def test_missing_expected_ok(tmp_path):
    data = [{"input": "hello"}]
    p    = tmp_path / "evals.json"
    p.write_text(json.dumps(data))
    ds = from_json(p)
    assert ds.cases[0].expected is None
