"""Reproducible, synthetic-only evaluation for the explicit baseline rules."""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from .log_matcher import event_matches
from .models import Rule, SecurityEvent
from .rules import generate_rules

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class EvaluationCase(BaseModel):
    scenario: str
    event: SecurityEvent
    expected_rule_ids: list[str] = Field(default_factory=list)


class RuleMetrics(BaseModel):
    rule_id: str
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float | None
    recall: float | None
    false_positive_rate: float | None


class EvaluationReport(BaseModel):
    dataset_name: str
    dataset_size: int
    metrics: list[RuleMetrics]
    limitations: str


def load_evaluation_cases() -> list[EvaluationCase]:
    raw = json.loads((DATA_DIR / "evaluation_cases.json").read_text(encoding="utf-8"))
    return [EvaluationCase.model_validate(case) for case in raw]


def safe_ratio(numerator: int, denominator: int) -> float | None:
    """Return None when a metric's denominator is zero rather than inventing a value."""
    return None if denominator == 0 else numerator / denominator


def evaluate_baseline() -> EvaluationReport:
    # This text activates both known patterns; labels come only from evaluation_cases.json.
    rules: list[Rule] = generate_rules("rundll32.exe powershell -enc")
    cases = load_evaluation_cases()
    metrics: list[RuleMetrics] = []
    for rule in rules:
        tp = fp = tn = fn = 0
        for case in cases:
            actual = event_matches(rule, case.event)
            expected = rule.id in case.expected_rule_ids
            if actual and expected:
                tp += 1
            elif actual:
                fp += 1
            elif expected:
                fn += 1
            else:
                tn += 1
        metrics.append(RuleMetrics(
            rule_id=rule.id, true_positives=tp, false_positives=fp,
            true_negatives=tn, false_negatives=fn,
            precision=safe_ratio(tp, tp + fp), recall=safe_ratio(tp, tp + fn),
            false_positive_rate=safe_ratio(fp, fp + tn),
        ))
    return EvaluationReport(
        dataset_name="bundled synthetic baseline evaluation",
        dataset_size=len(cases), metrics=metrics,
        limitations="Synthetic labels and scenarios are small, hand-authored, and not evidence of production detection performance.",
    )
