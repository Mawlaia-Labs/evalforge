from ..models import EvalCase, EvalResult
from .base import Scorer


def _lcs_length(a: list, b: list) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def rouge_l(hypothesis: str, reference: str) -> float:
    h = hypothesis.lower().split()
    r = reference.lower().split()
    if not h or not r:
        return 0.0
    lcs = _lcs_length(h, r)
    precision = lcs / len(h)
    recall    = lcs / len(r)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


class RougeScorer(Scorer):
    name = "rouge_l"

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def score(self, case: EvalCase, output: str) -> EvalResult:
        s = rouge_l(output, case.expected or "")
        return self._result(case, output, s, pass_threshold=self.threshold)
