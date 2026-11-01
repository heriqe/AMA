"""Typed data contracts shared by early AMA core components."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class CognitiveInput:
    """A structured input received by the cognitive core."""

    content: str
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
    received_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("content must not be empty")
        if not self.source.strip():
            raise ValueError("source must not be empty")


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """Result of a deterministic reasoning operation."""

    conclusions: tuple[dict[str, Any], ...]
    explanation: tuple[str, ...] = ()
    completed_at: datetime = field(default_factory=utc_now)
