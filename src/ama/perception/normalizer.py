"""Normalize structured observations without pretending to parse free text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ama.knowledge.models import Fact


@dataclass(frozen=True, slots=True)
class Observation:
    """A validated batch of facts received from one source."""

    source: str
    facts: tuple[Fact, ...]


def normalize_observation(payload: Mapping[str, Any]) -> Observation:
    """Convert a mapping with a source and facts list into validated Fact objects.

    Expected shape:
        {"source": "manual", "facts": [
            {"predicate": "platform", "value": "example", "confidence": 0.9}
        ]}

    This function validates structured data only. It does not extract meaning
    from natural-language paragraphs or verify the truth of supplied claims.
    """
    source = payload.get("source", "unknown")
    raw_facts = payload.get("facts")

    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")
    if not isinstance(raw_facts, list):
        raise ValueError("facts must be a list")

    facts: list[Fact] = []
    for index, item in enumerate(raw_facts):
        if not isinstance(item, Mapping):
            raise ValueError(f"facts[{index}] must be an object")
        if "predicate" not in item or "value" not in item:
            raise ValueError(f"facts[{index}] requires predicate and value")

        fact_source = item.get("source", source)
        confidence = item.get("confidence", 1.0)
        if not isinstance(fact_source, str):
            raise ValueError(f"facts[{index}].source must be a string")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError(f"facts[{index}].confidence must be numeric")

        facts.append(
            Fact(
                predicate=item["predicate"],
                value=item["value"],
                source=fact_source,
                confidence=float(confidence),
                valid_until=item.get("valid_until"),
            )
        )

    return Observation(source=source, facts=tuple(facts))
