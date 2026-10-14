from app.rules import generate_rules, rule_to_yaml
from app.validator import validate_rule_yaml


def test_generated_rule_is_valid():
    valid, errors, _ = validate_rule_yaml(rule_to_yaml(generate_rules("rundll32.exe")[0]))
    assert valid and not errors


def test_invalid_rule_is_rejected():
    valid, errors, _ = validate_rule_yaml("id: bad\ntitle: x\ndetection: []")
    assert not valid and errors


def test_malformed_yaml_and_unsupported_operator_are_rejected():
    valid, errors, _ = validate_rule_yaml("id: [")
    assert not valid and errors[0].startswith("Invalid YAML")
    valid, errors, _ = validate_rule_yaml("""id: unsupported-op
title: Unsupported operator
description: This should fail schema validation.
detection:
  - field: process_name
    operator: regex
    value: rundll32.exe
""")
    assert not valid
    assert any("Input should be 'equals' or 'contains'" in error for error in errors)
