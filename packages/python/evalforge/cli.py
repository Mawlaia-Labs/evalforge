"""evalforge CLI — evalforge run / evalforge compare"""
from __future__ import annotations
import json
import sys
import click
from .datasets import load
from .runner import run_eval
from .scorers import ExactMatchScorer, RougeScorer, RegexScorer, LLMJudgeScorer


def _scorer_from_name(name: str, threshold: float) -> object:
    if name == "exact":
        return ExactMatchScorer()
    if name == "rouge":
        return RougeScorer(threshold=threshold)
    if name.startswith("llm"):
        parts  = name.split(":")              # e.g. "llm:gpt-4o-mini"
        model  = parts[1] if len(parts) > 1 else "gpt-4o-mini"
        return LLMJudgeScorer(model=model, threshold=threshold)
    if name.startswith("regex:"):
        return RegexScorer(name.split(":", 1)[1])
    raise click.BadParameter(f"Unknown scorer: {name}")


@click.group()
def cli():
    """evalforge — eval runner for LLM applications."""


@cli.command()
@click.option("--dataset",   "-d", required=True, help="Path to .json/.jsonl/.csv eval dataset")
@click.option("--scorer",    "-s", default="exact", help="Scorer: exact | rouge | llm[:model] | regex:<pattern>")
@click.option("--outputs",   "-o", default=None, help="Path to pre-generated outputs (.jsonl, one per line)")
@click.option("--threshold", "-t", default=0.5, type=float, help="Pass threshold (default 0.5)")
@click.option("--json",      "as_json", is_flag=True, help="Output results as JSON")
def run(dataset, scorer, outputs, threshold, as_json):
    """Run evaluation on a dataset."""
    ds      = load(dataset)
    sc      = _scorer_from_name(scorer, threshold)

    out_list = None
    if outputs:
        out_list = [line.strip() for line in open(outputs).readlines() if line.strip()]

    report = run_eval(ds, sc, outputs=out_list, pass_threshold=threshold)

    if as_json:
        click.echo(json.dumps({
            "scorer":    report.scorer_name,
            "mean_score": report.mean_score,
            "pass_rate":  report.pass_rate,
            "n_cases":    len(report.results),
            "n_failed":   len(report.failed),
        }, indent=2))
    else:
        click.echo(report.summary())

    sys.exit(0 if report.pass_rate >= threshold else 1)


@cli.command()
@click.option("--dataset",   "-d", required=True)
@click.option("--baseline",  "-b", required=True, help="Baseline outputs file (.jsonl)")
@click.option("--candidate", "-c", required=True, help="Candidate outputs file (.jsonl)")
@click.option("--scorer",    "-s", default="rouge")
@click.option("--threshold", "-t", default=0.5, type=float)
def diff(dataset, baseline, candidate, scorer, threshold):
    """Compare two output sets against the same dataset."""
    ds       = load(dataset)
    sc       = _scorer_from_name(scorer, threshold)
    base_out = [line.strip() for line in open(baseline).readlines() if line.strip()]
    cand_out = [line.strip() for line in open(candidate).readlines() if line.strip()]

    base_r   = run_eval(ds, sc, outputs=base_out, pass_threshold=threshold)
    cand_r   = run_eval(ds, sc, outputs=cand_out, pass_threshold=threshold)
    delta    = cand_r.mean_score - base_r.mean_score

    click.echo(f"Baseline  : {base_r.mean_score:.3f} ({base_r.pass_rate:.0%} pass)")
    click.echo(f"Candidate : {cand_r.mean_score:.3f} ({cand_r.pass_rate:.0%} pass)")
    click.echo(f"Delta     : {delta:+.3f}")
    sys.exit(0 if delta >= 0 else 1)


def main():
    cli()
