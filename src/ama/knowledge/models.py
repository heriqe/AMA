"""Validated knowledge facts with provenance and confidence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _validate_timestamp(value: str, field_name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from error


@dataclass(frozen=True, slots=True)
class Fact:
    """An explicit claim stored with its origin and confidence.

    Confidence is metadata supplied by the caller; it is not a calibrated
    probability and must not be interpreted as proof that a claim is true.
    """

    predicate: str
    value: Any
    source: str
    confidence: float = 1.0
    fact_id: str = field(default_factory=lambda: str(uuid4()))
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    valid_until: str | None = None

    def __post_init__(self) -> None:
        if not self.predicate.strip():
            raise ValueError("predicate must not be empty")
        if not self.source.strip():
            raise ValueError("source must not be empty")
        if not self.fact_id.strip():
            raise ValueError("fact_id must not be empty")
        if isinstance(self.confidence, bool) or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be a number between 0 and 1")
        _validate_timestamp(self.observed_at, "observed_at")
        if self.valid_until is not None:
            _validate_timestamp(self.valid_until, "valid_until")
        try:
            json.dumps(self.value, ensure_ascii=False)
        except (TypeError, ValueError) as error:
            raise ValueError("fact value must be JSON serializable") from error
