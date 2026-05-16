from __future__ import annotations
from typing import Callable
from ..models import EvalCase, EvalResult
from .base import Scorer


class CustomScorer(Scorer):
    """Wraps an arbitrary Python function: fn(case, output) -> float."""
    name = "custom"

    def __init__(self, fn: Callable[[EvalCase, str], float], threshold: float = 0.5):
        self.fn        = fn
        self.threshold = threshold

    def score(self, case: EvalCase, output: str) -> EvalResult:
        s = float(self.fn(case, output))
        return self._result(case, output, s, pass_threshold=self.threshold)
