from abc import ABC, abstractmethod
from ..models import EvalCase, EvalResult


class Scorer(ABC):
    name: str = "base"

    @abstractmethod
    def score(self, case: EvalCase, output: str) -> EvalResult:
        ...

    def _result(
        self,
        case: EvalCase,
        output: str,
        score: float,
        pass_threshold: float = 0.5,
        reason: str | None = None,
    ) -> EvalResult:
        return EvalResult(
            case=case,
            output=output,
            score=score,
            passed=score >= pass_threshold,
            reason=reason,
        )
