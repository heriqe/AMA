"""Structured, serializable records explaining deterministic inferences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class InferenceRecord:
    """One rule firing, including the exact premises and produced conclusion."""

    sequence: int
    rule_name: str
    premises: tuple[tuple[str, Any], ...]
    conclusion_key: str
    conclusion_value: Any


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Facts produced by a rule pass and its ordered explanation trace."""

    facts: dict[str, Any]
    trace: tuple[InferenceRecord, ...]

    @property
    def fired_rules(self) -> tuple[str, ...]:
        return tuple(record.rule_name for record in self.trace)
