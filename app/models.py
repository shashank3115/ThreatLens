from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceRef(BaseModel):
    reference: str
    excerpt: str


class Condition(BaseModel):
    field: Literal["process_name", "command_line", "event_type", "user", "host"]
    operator: Literal["equals", "contains"]
    value: str = Field(min_length=1, max_length=500)


class Rule(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=3, max_length=500)
    detection: list[Condition] = Field(min_length=1, max_length=10)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    timestamp: str
    host: str
    user: str
    event_type: str
    process_name: str
    command_line: str
    label: Literal["suspicious", "benign"]


class AnalyzeRequest(BaseModel):
    report: str = Field(min_length=1, max_length=20_000)

    @field_validator("report")
    @classmethod
    def report_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Report must contain non-whitespace text.")
        return value


class RuleResult(BaseModel):
    rule: Rule
    yaml: str
    structural_valid: bool
    validation_errors: list[str]
    evidence_supported: bool
    unsupported_reason: str | None = None
    suspicious_event_ids: list[str]
    benign_event_ids: list[str]
    false_positive_warning: str | None = None


class AnalyzeResponse(BaseModel):
    report_length: int
    extracted_evidence: list[EvidenceRef]
    rules: list[RuleResult]
    summary: dict[str, Any]
