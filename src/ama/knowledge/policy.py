"""Deterministic policies for assessing stored knowledge facts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from ama.knowledge.models import Fact


@dataclass(frozen=True, slots=True)
class FactAssessment:
    """Explain how one fact was treated by the knowledge policy."""

    fact_id: str
    predicate: str
    status: str
    reason: str


@dataclass(frozen=True, slots=True)
class ResolvedFact:
    """A predicate value supported by one or more non-conflicting facts."""

    predicate: str
    value: object
    source_fact_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class KnowledgeAssessment:
    """Complete, auditable assessment of a collection of facts."""

    assessments: tuple[FactAssessment, ...]
    resolved: tuple[ResolvedFact, ...]

    def as_mapping(self) -> dict[str, object]:
        """Return unambiguous predicate/value pairs for deterministic rules."""
        return {item.predicate: item.value for item in self.resolved}


class KnowledgePolicy:
    """Filter stale/weak facts and refuse to guess when values conflict.

    Confidence is treated only as source-supplied metadata. It is not calibrated
    probability. Conflicting eligible values are deliberately left unresolved.
    """

    def __init__(self, *, minimum_confidence: float = 0.5) -> None:
        if (
            isinstance(minimum_confidence, bool)
            or not isinstance(minimum_confidence, (int, float))
            or not 0.0 <= minimum_confidence <= 1.0
        ):
            raise ValueError("minimum_confidence must be between 0 and 1")
        self.minimum_confidence = float(minimum_confidence)

    @staticmethod
    def _timestamp(value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _value_key(value: object) -> str:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)

    def assess(
        self,
        facts: Iterable[Fact],
        *,
        now: datetime | None = None,
    ) -> KnowledgeAssessment:
        """Classify facts and resolve only predicates without eligible conflicts."""
        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        current_time = current_time.astimezone(timezone.utc)

        fact_list = tuple(facts)
        groups: dict[str, list[Fact]] = {}
        statuses: dict[str, FactAssessment] = {}

        for fact in fact_list:
            if fact.valid_until is not None and self._timestamp(fact.valid_until) <= current_time:
                statuses[fact.fact_id] = FactAssessment(
                    fact.fact_id, fact.predicate, "expired", "valid_until is not later than now"
                )
            elif fact.confidence < self.minimum_confidence:
                statuses[fact.fact_id] = FactAssessment(
                    fact.fact_id,
                    fact.predicate,
                    "low_confidence",
                    f"confidence is below policy threshold {self.minimum_confidence}",
                )
            else:
                groups.setdefault(fact.predicate, []).append(fact)

        resolved: list[ResolvedFact] = []
        for predicate, candidates in groups.items():
            by_value: dict[str, list[Fact]] = {}
            for fact in candidates:
                by_value.setdefault(self._value_key(fact.value), []).append(fact)

            if len(by_value) > 1:
                for fact in candidates:
                    statuses[fact.fact_id] = FactAssessment(
                        fact.fact_id,
                        predicate,
                        "conflict",
                        "multiple eligible values exist for this predicate",
                    )
                continue

            supporting_facts = next(iter(by_value.values()))
            for fact in supporting_facts:
                statuses[fact.fact_id] = FactAssessment(
                    fact.fact_id, predicate, "accepted", "eligible and not contradicted"
                )
            resolved.append(
                ResolvedFact(
                    predicate=predicate,
                    value=supporting_facts[0].value,
                    source_fact_ids=tuple(fact.fact_id for fact in supporting_facts),
                )
            )

        ordered_assessments = tuple(statuses[fact.fact_id] for fact in fact_list)
        return KnowledgeAssessment(ordered_assessments, tuple(resolved))
