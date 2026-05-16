from __future__ import annotations
from ..models import EvalCase, EvalResult
from .base import Scorer


def _cosine(a: list[float], b: list[float]) -> float:
    dot  = sum(x * y for x, y in zip(a, b))
    na   = sum(x * x for x in a) ** 0.5
    nb   = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SemanticScorer(Scorer):
    """Cosine similarity between sentence embeddings.

    Requires sentence-transformers (optional dependency).
    Falls back gracefully if not installed.
    """
    name = "semantic"

    def __init__(self, model: str = "all-MiniLM-L6-v2", threshold: float = 0.8):
        self.threshold = threshold
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model)
        except ImportError:
            self._model = None

    def score(self, case: EvalCase, output: str) -> EvalResult:
        if self._model is None:
            raise RuntimeError(
                "SemanticScorer requires sentence-transformers: "
                "pip install sentence-transformers"
            )
        vecs  = self._model.encode([output, case.expected or ""])
        s     = float(_cosine(vecs[0].tolist(), vecs[1].tolist()))
        return self._result(case, output, s, pass_threshold=self.threshold)
