"""Deterministic, offline quality metrics for LLM output files."""

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

SUPPORTED_GATE_METRICS = ("exact_match", "token_f1", "character_f1")


def normalize_text(value: Any) -> str:
    """Normalize text for case-insensitive, whitespace-tolerant comparisons."""
    if value is None:
        return ""
    return " ".join(str(value).casefold().split())


def _sequence_f1(expected_items: Sequence[str], actual_items: Sequence[str]) -> float:
    if not expected_items or not actual_items:
        return 0.0

    overlap = sum((Counter(expected_items) & Counter(actual_items)).values())
    precision = overlap / len(actual_items)
    recall = overlap / len(expected_items)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def token_f1(expected: Any, actual: Any) -> float:
    """Return token-level F1 using whitespace-separated, normalized tokens."""
    expected_tokens = normalize_text(expected).split()
    actual_tokens = normalize_text(actual).split()
    return _sequence_f1(expected_tokens, actual_tokens)


def character_f1(expected: Any, actual: Any) -> float:
    """Return F1 over normalized non-whitespace Unicode characters."""
    expected_chars = [char for char in normalize_text(expected) if not char.isspace()]
    actual_chars = [char for char in normalize_text(actual) if not char.isspace()]
    return _sequence_f1(expected_chars, actual_chars)


def _exact_match(expected: Any, actual: Any) -> float:
    return float(normalize_text(expected) == normalize_text(actual))


def load_records(
    path: str,
    expected_field: str = "expected",
    actual_field: str = "actual",
    id_field: str = "id",
) -> List[Dict[str, Any]]:
    """Load and validate one JSON object per non-empty JSONL line."""
    records: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc.msg}"
                ) from exc

            if not isinstance(record, dict):
                raise ValueError(f"Expected a JSON object on line {line_number}")

            missing = [
                field for field in (expected_field, actual_field) if field not in record
            ]
            if missing:
                fields = ", ".join(missing)
                raise ValueError(
                    f"Missing required field(s) on line {line_number}: {fields}"
                )

            if id_field not in record:
                record[id_field] = len(records) + 1
            records.append(record)
    return records


def evaluate_records(
    records: Sequence[Mapping[str, Any]],
    expected_field: str = "expected",
    actual_field: str = "actual",
    id_field: str = "id",
) -> Dict[str, Any]:
    """Calculate aggregate and per-record deterministic quality scores."""
    scored_records = []
    for index, record in enumerate(records, start=1):
        missing = [
            field for field in (expected_field, actual_field) if field not in record
        ]
        if missing:
            fields = ", ".join(missing)
            raise ValueError(f"Missing required field(s) in record {index}: {fields}")

        expected = record[expected_field]
        actual = record[actual_field]
        scored_records.append(
            {
                "id": record.get(id_field, index),
                "exact_match": _exact_match(expected, actual),
                "token_f1": token_f1(expected, actual),
                "character_f1": character_f1(expected, actual),
            }
        )

    samples = len(scored_records)
    if samples == 0:
        exact_match = token_f1_score = character_f1_score = 0.0
    else:
        exact_match = sum(item["exact_match"] for item in scored_records) / samples
        token_f1_score = sum(item["token_f1"] for item in scored_records) / samples
        character_f1_score = (
            sum(item["character_f1"] for item in scored_records) / samples
        )

    return {
        "samples": samples,
        "exact_match": exact_match,
        "token_f1": token_f1_score,
        "character_f1": character_f1_score,
        "records": scored_records,
    }


def compare_evaluations(
    candidate: Mapping[str, Any],
    baseline: Optional[Mapping[str, Any]] = None,
    gate_metric: str = "token_f1",
    min_score: Optional[float] = None,
    min_improvement: float = 0.0,
) -> Dict[str, Any]:
    """Compare a candidate report with an optional baseline and apply gates."""
    if gate_metric not in SUPPORTED_GATE_METRICS:
        choices = ", ".join(SUPPORTED_GATE_METRICS)
        raise ValueError(f"Unsupported gate metric {gate_metric!r}; choose: {choices}")

    failures: List[str] = []
    delta = None
    if baseline is not None:
        if candidate["samples"] != baseline["samples"]:
            raise ValueError(
                "Candidate and baseline sample counts differ: "
                f"{candidate['samples']} != {baseline['samples']}"
            )

        delta = {
            metric: round(candidate[metric] - baseline[metric], 10)
            for metric in SUPPORTED_GATE_METRICS
        }
        metric_delta = delta[gate_metric]
        if metric_delta < min_improvement:
            if metric_delta < 0:
                failures.append(
                    f"{gate_metric} regressed by "
                    f"{abs(metric_delta):.4f} from baseline"
                )
            else:
                failures.append(
                    f"{gate_metric} improvement "
                    f"{metric_delta:.4f} is below required "
                    f"{min_improvement:.4f}"
                )

    if min_score is not None and candidate[gate_metric] < min_score:
        failures.append(
            f"{gate_metric} {candidate[gate_metric]:.4f} is below required "
            f"{min_score:.4f}"
        )

    result = {
        "samples": candidate["samples"],
        "exact_match": candidate["exact_match"],
        "token_f1": candidate["token_f1"],
        "character_f1": candidate["character_f1"],
        "records": candidate.get("records", []),
        "candidate": dict(candidate),
        "baseline": dict(baseline) if baseline is not None else None,
        "delta": delta,
        "gate": {
            "metric": gate_metric,
            "min_score": min_score,
            "min_improvement": min_improvement,
        },
        "passed": not failures,
        "failures": failures,
    }
    return result
