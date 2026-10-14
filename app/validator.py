from __future__ import annotations
import yaml
from pydantic import ValidationError
from .models import Rule


def validate_rule_yaml(rule_yaml: str) -> tuple[bool, list[str], Rule | None]:
    """Check YAML syntax then our deliberately small rule schema."""
    try:
        raw = yaml.safe_load(rule_yaml)
    except yaml.YAMLError as exc:
        return False, [f"Invalid YAML: {exc}"], None
    try:
        return True, [], Rule.model_validate(raw)
    except ValidationError as exc:
        return False, [item["msg"] for item in exc.errors()], None
