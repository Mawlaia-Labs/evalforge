"""evalforge — eval runner for LLM applications."""

from .models  import EvalCase, EvalDataset, EvalResult, EvalReport
from .runner  import run_eval, compare
from .scorers import (
    Scorer, ExactMatchScorer, RegexScorer, RougeScorer,
    SemanticScorer, LLMJudgeScorer, CustomScorer,
)
from .datasets import load as load_dataset

__version__ = "0.1.0"

__all__ = [
    "EvalCase", "EvalDataset", "EvalResult", "EvalReport",
    "run_eval", "compare", "load_dataset",
    "Scorer", "ExactMatchScorer", "RegexScorer", "RougeScorer",
    "SemanticScorer", "LLMJudgeScorer", "CustomScorer",
]
