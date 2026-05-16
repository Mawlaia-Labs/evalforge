from evalforge.models import EvalCase, EvalDataset, EvalResult, EvalReport


def test_eval_case_defaults():
    c = EvalCase(input="hello")
    assert c.expected is None
    assert c.metadata == {}
    assert c.tags == []


def test_eval_dataset_len_iter():
    ds = EvalDataset(cases=[
        EvalCase(input="a", expected="b"),
        EvalCase(input="c", expected="d"),
    ])
    assert len(ds) == 2
    assert list(ds)[0].input == "a"


def test_eval_dataset_filter():
    ds = EvalDataset(cases=[
        EvalCase(input="a", tags=["rag"]),
        EvalCase(input="b", tags=["qa"]),
        EvalCase(input="c", tags=["rag", "qa"]),
    ])
    assert len(ds.filter("rag")) == 2
    assert len(ds.filter("qa"))  == 2
    assert len(ds.filter("xyz")) == 0


def test_eval_result_score_clamped():
    case = EvalCase(input="x")
    r    = EvalResult(case=case, output="y", score=1.5, passed=True)
    assert r.score == 1.0
    r2   = EvalResult(case=case, output="y", score=-0.1, passed=False)
    assert r2.score == 0.0


def test_eval_report_summary():
    case    = EvalCase(input="x", expected="y")
    results = [
        EvalResult(case=case, output="y",   score=1.0, passed=True),
        EvalResult(case=case, output="bad", score=0.0, passed=False),
    ]
    report  = EvalReport(results=results, scorer_name="exact_match")
    assert report.mean_score == 0.5
    assert report.pass_rate  == 0.5
    assert len(report.failed) == 1
    assert "exact_match" in report.summary()


def test_eval_report_empty():
    report = EvalReport(results=[], scorer_name="test")
    assert report.mean_score == 0.0
    assert report.pass_rate  == 0.0
