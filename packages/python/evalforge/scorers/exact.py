from ..models import EvalCase, EvalResult
from .base import Scorer


class ExactMatchScorer(Scorer):
    name = "exact_match"

    def __init__(self, case_sensitive: bool = False, strip: bool = True):
        self.case_sensitive = case_sensitive
        self.strip          = strip

    def score(self, case: EvalCase, output: str) -> EvalResult:
        expected = case.expected or ""
        a, b = output, expected
        if self.strip:
            a, b = a.strip(), b.strip()
        if not self.case_sensitive:
            a, b = a.lower(), b.lower()
        match = a == b
        return self._result(case, output, 1.0 if match else 0.0, reason=None)
