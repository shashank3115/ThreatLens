from app.log_matcher import match_events
from app.rules import generate_rules
from app.service import load_sample_events
from app.models import SecurityEvent
from pydantic import ValidationError


def test_rule_matches_suspicious_and_benign_examples():
    suspicious, benign = match_events(generate_rules("rundll32.exe")[0], load_sample_events())
    assert suspicious == ["evt-001"]
    assert benign == ["evt-003"]


def test_unexpected_event_fields_are_rejected():
    event = load_sample_events()[0].model_dump()
    event["unexpected_field"] = "not silently accepted"
    try:
        SecurityEvent.model_validate(event)
    except ValidationError as exc:
        assert "unexpected_field" in str(exc)
    else:
        raise AssertionError("Unexpected fields must be rejected")
