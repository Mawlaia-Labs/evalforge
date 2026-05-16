import re
from ..models import EvalCase, EvalResult
from .base import Scorer


class RegexScorer(Scorer):
    name = "regex"

    def __init__(self, pattern: str, flags: int = re.IGNORECASE):
        self._re = re.compile(pattern, flags)

    def score(self, case: EvalCase, output: str) -> EvalResult:
        match = bool(self._re.search(output))
        return self._result(case, output, 1.0 if match else 0.0)
