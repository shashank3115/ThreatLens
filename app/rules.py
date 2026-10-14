"""Explicit report patterns used by the deterministic baseline."""
from __future__ import annotations
import yaml
from .evidence import find_evidence
from .models import Condition, EvidenceRef, Rule

PATTERNS = (
    {
        "term": "rundll32.exe",
        "id": "tl-rundll32-execution",
        "title": "Rundll32 execution observed",
        "description": "Flags process creation where rundll32.exe is used.",
        "conditions": [Condition(field="process_name", operator="equals", value="rundll32.exe")],
    },
    {
        "term": "powershell -enc",
        "id": "tl-encoded-powershell",
        "title": "Encoded PowerShell command observed",
        "description": "Flags command lines containing the explicitly reported PowerShell encoding switch.",
        "conditions": [Condition(field="command_line", operator="contains", value="powershell -enc")],
    },
)


def generate_rules(report: str) -> list[Rule]:
    rules: list[Rule] = []
    for pattern in PATTERNS:
        evidence = find_evidence(report, [pattern["term"]])
        rules.append(Rule(id=pattern["id"], title=pattern["title"], description=pattern["description"],
                          detection=pattern["conditions"], evidence_refs=evidence))
    return rules


def rule_to_yaml(rule: Rule) -> str:
    return yaml.safe_dump(rule.model_dump(mode="json"), sort_keys=False, allow_unicode=True)
