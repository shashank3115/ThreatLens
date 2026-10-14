"""Small, explainable evidence extraction helpers."""
from __future__ import annotations
import re
from .models import EvidenceRef


def split_passages(report: str) -> list[str]:
    """Split prose into stable sentence-like passages, ignoring blank fragments."""
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", report) if part.strip()]


def find_evidence(report: str, terms: list[str]) -> list[EvidenceRef]:
    """Return passages containing a requested literal term (case-insensitive)."""
    results: list[EvidenceRef] = []
    for index, passage in enumerate(split_passages(report), start=1):
        if any(term.lower() in passage.lower() for term in terms):
            results.append(EvidenceRef(reference=f"passage-{index}", excerpt=passage))
    return results
