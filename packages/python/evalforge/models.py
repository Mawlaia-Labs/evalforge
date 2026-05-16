from __future__ import annotations
from typing import Any
from pydantic import BaseModel, field_validator


class EvalCase(BaseModel):
    input:    str
    expected: str | None = None
    metadata: dict[str, Any] = {}
    tags:     list[str]     = []


class EvalResult(BaseModel):
    case:     EvalCase
    output:   str
    score:    float          # 0.0–1.0
    passed:   bool
    reason:   str | None = None
    metadata: dict[str, Any] = {}

    @field_validator("score")
    @classmethod
    def clamp(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class EvalReport(BaseModel):
    results:     list[EvalResult]
    scorer_name: str
    pass_threshold: float = 0.5

    @property
    def mean_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    @property
    def failed(self) -> list[EvalResult]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        n = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        return (
            f"Scorer : {self.scorer_name}\n"
            f"Cases  : {n}\n"
            f"Passed : {passed}/{n} ({self.pass_rate:.0%})\n"
            f"Score  : {self.mean_score:.3f}"
        )


class EvalDataset(BaseModel):
    cases: list[EvalCase]
    name:  str = "unnamed"

    def __len__(self) -> int:
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def filter(self, tag: str) -> "EvalDataset":
        return EvalDataset(
            cases=[c for c in self.cases if tag in c.tags],
            name=self.name,
        )
