from __future__ import annotations
import csv
import json
from pathlib import Path
from ..models import EvalCase, EvalDataset


def _case_from_dict(d: dict) -> EvalCase:
    return EvalCase(
        input=d["input"],
        expected=d.get("expected") or d.get("expected_output"),
        metadata=d.get("metadata", {}),
        tags=d.get("tags", []),
    )


def from_json(path: str | Path) -> EvalDataset:
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        cases = [_case_from_dict(d) for d in data]
    else:
        cases = [_case_from_dict(d) for d in data["cases"]]
        return EvalDataset(cases=cases, name=data.get("name", Path(path).stem))
    return EvalDataset(cases=cases, name=Path(path).stem)


def from_jsonl(path: str | Path) -> EvalDataset:
    cases = [_case_from_dict(json.loads(line)) for line in Path(path).read_text().splitlines() if line.strip()]
    return EvalDataset(cases=cases, name=Path(path).stem)


def from_csv(path: str | Path) -> EvalDataset:
    cases = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(_case_from_dict(dict(row)))
    return EvalDataset(cases=cases, name=Path(path).stem)


def load(path: str | Path) -> EvalDataset:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return from_json(path)
    if suffix == ".jsonl":
        return from_jsonl(path)
    if suffix == ".csv":
        return from_csv(path)
    raise ValueError(f"Unsupported format: {suffix}. Use .json, .jsonl, or .csv")
