import pytest
from evalforge.models import EvalCase, EvalDataset
from evalforge.runner import run_eval, compare
from evalforge.scorers import ExactMatchScorer


def make_dataset(*pairs):
    return EvalDataset(cases=[EvalCase(input=q, expected=a) for q, a in pairs])


# ── run_eval with pre-generated outputs ──────────────────────────────────────

def test_run_eval_with_outputs():
    ds     = make_dataset(("What is 2+2?", "4"), ("Capital of France?", "Paris"))
    report = run_eval(ds, ExactMatchScorer(), outputs=["4", "Paris"])
    assert report.pass_rate == 1.0
    assert report.mean_score == 1.0

def test_run_eval_partial_pass():
    ds     = make_dataset(("q1", "yes"), ("q2", "no"))
    report = run_eval(ds, ExactMatchScorer(), outputs=["yes", "wrong"])
    assert report.pass_rate == 0.5

def test_run_eval_with_model_fn():
    ds     = make_dataset(("ping", "pong"))
    report = run_eval(ds, ExactMatchScorer(), model_fn=lambda q: "pong")
    assert report.pass_rate == 1.0

def test_run_eval_requires_model_or_outputs():
    ds = make_dataset(("q", "a"))
    with pytest.raises(ValueError):
        run_eval(ds, ExactMatchScorer())

def test_run_eval_outputs_length_mismatch():
    ds = make_dataset(("q1", "a"), ("q2", "b"))
    with pytest.raises(ValueError):
        run_eval(ds, ExactMatchScorer(), outputs=["only one"])

def test_run_eval_pass_threshold():
    ds     = make_dataset(("q", "a"))
    report = run_eval(ds, ExactMatchScorer(), outputs=["a"], pass_threshold=0.9)
    # ExactMatchScorer returns 1.0, so still passes
    assert report.results[0].passed

def test_run_eval_empty_dataset():
    ds     = EvalDataset(cases=[])
    report = run_eval(ds, ExactMatchScorer(), outputs=[])
    assert report.mean_score == 0.0
    assert report.pass_rate  == 0.0


# ── compare ───────────────────────────────────────────────────────────────────

def test_compare():
    ds           = make_dataset(("Capital of France?", "Paris"))
    base_report, cand_report = compare(
        ds,
        ExactMatchScorer(),
        baseline=lambda q: "Lyon",
        candidate=lambda q: "Paris",
    )
    assert base_report.pass_rate  == 0.0
    assert cand_report.pass_rate  == 1.0
