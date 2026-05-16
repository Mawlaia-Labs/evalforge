import pytest
from evalforge.models import EvalCase
from evalforge.scorers import (
    ExactMatchScorer, RegexScorer, RougeScorer, CustomScorer, LLMJudgeScorer
)


def case(input: str, expected: str) -> EvalCase:
    return EvalCase(input=input, expected=expected)


# ── ExactMatchScorer ─────────────────────────────────────────────────────────

def test_exact_match_pass():
    r = ExactMatchScorer().score(case("q", "Paris"), "Paris")
    assert r.score == 1.0 and r.passed

def test_exact_match_fail():
    r = ExactMatchScorer().score(case("q", "Paris"), "Lyon")
    assert r.score == 0.0 and not r.passed

def test_exact_match_case_insensitive():
    r = ExactMatchScorer(case_sensitive=False).score(case("q", "Paris"), "paris")
    assert r.score == 1.0

def test_exact_match_case_sensitive():
    r = ExactMatchScorer(case_sensitive=True).score(case("q", "Paris"), "paris")
    assert r.score == 0.0

def test_exact_match_strips():
    r = ExactMatchScorer().score(case("q", "Paris"), "  Paris  ")
    assert r.score == 1.0


# ── RegexScorer ───────────────────────────────────────────────────────────────

def test_regex_match():
    r = RegexScorer(r"\d{3}-\d{4}").score(case("q", ""), "Call 555-1234 now")
    assert r.score == 1.0 and r.passed

def test_regex_no_match():
    r = RegexScorer(r"\d{3}-\d{4}").score(case("q", ""), "No number here")
    assert r.score == 0.0


# ── RougeScorer ───────────────────────────────────────────────────────────────

def test_rouge_perfect():
    r = RougeScorer().score(case("q", "the cat sat on the mat"), "the cat sat on the mat")
    assert r.score == pytest.approx(1.0)

def test_rouge_empty_output():
    r = RougeScorer().score(case("q", "hello world"), "")
    assert r.score == 0.0

def test_rouge_partial():
    r = RougeScorer(threshold=0.3).score(case("q", "the cat sat on the mat"), "the cat")
    assert 0.3 < r.score < 1.0
    assert r.passed

def test_rouge_threshold():
    r = RougeScorer(threshold=0.9).score(case("q", "the quick brown fox"), "the quick")
    assert not r.passed


# ── CustomScorer ──────────────────────────────────────────────────────────────

def test_custom_scorer():
    scorer = CustomScorer(fn=lambda c, o: 1.0 if len(o) > 5 else 0.0)
    r = scorer.score(case("q", "anything"), "long output")
    assert r.score == 1.0 and r.passed
    r2 = scorer.score(case("q", "anything"), "hi")
    assert r2.score == 0.0


# ── LLMJudgeScorer (mocked) ──────────────────────────────────────────────────

def test_llm_judge_parses_response(monkeypatch):
    scorer = LLMJudgeScorer(model="gpt-4o-mini")

    def fake_call(self, prompt):
        return '{"score": 0.9, "reason": "Correct and complete."}'

    monkeypatch.setattr(LLMJudgeScorer, "_call", fake_call)
    r = scorer.score(case("What is 2+2?", "4"), "4")
    assert r.score == pytest.approx(0.9)
    assert r.passed
    assert "Correct" in r.reason

def test_llm_judge_bad_json_graceful(monkeypatch):
    scorer = LLMJudgeScorer(model="gpt-4o-mini")
    monkeypatch.setattr(LLMJudgeScorer, "_call", lambda self, p: "oops not json")
    r = scorer.score(case("q", "a"), "b")
    assert r.score == 0.0
    assert not r.passed
