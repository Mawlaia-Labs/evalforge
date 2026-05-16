from __future__ import annotations
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import EvalCase, EvalDataset, EvalReport
from .scorers.base import Scorer


ModelFn = Callable[[str], str]


def run_eval(
    dataset:        EvalDataset,
    scorer:         Scorer,
    model_fn:       ModelFn | None    = None,
    outputs:        list[str] | None  = None,
    pass_threshold: float             = 0.5,
    max_workers:    int               = 4,
) -> EvalReport:
    """Run an evaluation.

    Supply either `model_fn` (called per case to generate outputs) or
    pre-generated `outputs` (list aligned with dataset.cases).
    """
    if model_fn is None and outputs is None:
        raise ValueError("Provide either model_fn or outputs")
    if outputs is not None and len(outputs) != len(dataset.cases):
        raise ValueError(f"outputs length {len(outputs)} != dataset length {len(dataset)}")

    if outputs is None:
        outputs = _generate(dataset.cases, model_fn, max_workers)  # type: ignore[arg-type]

    results = [scorer.score(case, out) for case, out in zip(dataset.cases, outputs)]

    # Respect pass_threshold override per report (individual scorers set their own internally)
    for r in results:
        r.passed = r.score >= pass_threshold

    return EvalReport(
        results=results,
        scorer_name=scorer.name,
        pass_threshold=pass_threshold,
    )


def compare(
    dataset:   EvalDataset,
    scorer:    Scorer,
    baseline:  ModelFn,
    candidate: ModelFn,
    max_workers: int = 4,
) -> tuple[EvalReport, EvalReport]:
    """Run eval on two model functions and return (baseline_report, candidate_report)."""
    base_outputs = _generate(dataset.cases, baseline,  max_workers)
    cand_outputs = _generate(dataset.cases, candidate, max_workers)
    base_report  = run_eval(dataset, scorer, outputs=base_outputs)
    cand_report  = run_eval(dataset, scorer, outputs=cand_outputs)
    return base_report, cand_report


def _generate(cases: list[EvalCase], fn: ModelFn, max_workers: int) -> list[str]:
    outputs: list[str] = [""] * len(cases)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fn, c.input): i for i, c in enumerate(cases)}
        for fut in as_completed(futures):
            outputs[futures[fut]] = fut.result()
    return outputs
