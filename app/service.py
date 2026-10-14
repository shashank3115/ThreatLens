from __future__ import annotations
import json
from pathlib import Path
from .evidence import find_evidence
from .log_matcher import match_events
from .models import AnalyzeResponse, RuleResult, SecurityEvent
from .rules import generate_rules, rule_to_yaml
from .validator import validate_rule_yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_sample_report() -> str:
    return (DATA_DIR / "sample_report.txt").read_text(encoding="utf-8")


def load_sample_events() -> list[SecurityEvent]:
    raw = json.loads((DATA_DIR / "sample_logs.json").read_text(encoding="utf-8"))
    return [SecurityEvent.model_validate(item) for item in raw]


def analyze_report(report: str) -> AnalyzeResponse:
    events = load_sample_events()
    results: list[RuleResult] = []
    for rule in generate_rules(report):
        rendered = rule_to_yaml(rule)
        valid, errors, _ = validate_rule_yaml(rendered)
        suspicious, benign = match_events(rule, events)
        supported = bool(rule.evidence_refs)
        results.append(RuleResult(
            rule=rule, yaml=rendered, structural_valid=valid, validation_errors=errors,
            evidence_supported=supported,
            unsupported_reason=None if supported else "No matching passage was found in the submitted report.",
            suspicious_event_ids=suspicious, benign_event_ids=benign,
            false_positive_warning=("Matched benign sample event(s): " + ", ".join(benign)) if benign else None,
        ))
    evidence = find_evidence(report, ["rundll32.exe", "powershell -enc"])
    return AnalyzeResponse(report_length=len(report), extracted_evidence=evidence, rules=results,
        summary={"candidate_rules": len(results), "structurally_valid": sum(r.structural_valid for r in results),
                 "evidence_supported": sum(r.evidence_supported for r in results),
                 "rules_with_benign_matches": sum(bool(r.benign_event_ids) for r in results)})
