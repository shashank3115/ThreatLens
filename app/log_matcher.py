from __future__ import annotations
from .models import Rule, SecurityEvent


def event_matches(rule: Rule, event: SecurityEvent) -> bool:
    for condition in rule.detection:
        actual = getattr(event, condition.field)
        if condition.operator == "equals" and actual.lower() != condition.value.lower():
            return False
        if condition.operator == "contains" and condition.value.lower() not in actual.lower():
            return False
    return True


def match_events(rule: Rule, events: list[SecurityEvent]) -> tuple[list[str], list[str]]:
    matched = [event for event in events if event_matches(rule, event)]
    return ([event.event_id for event in matched if event.label == "suspicious"],
            [event.event_id for event in matched if event.label == "benign"])
