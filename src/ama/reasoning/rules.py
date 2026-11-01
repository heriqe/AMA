"""A minimal, explainable forward-chaining rule engine.

Rules use explicit key/value facts. No eval, dynamic code execution, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ama.reasoning.models import InferenceResult, InferenceRecord


@dataclass(frozen=True, slots=True)
class Rule:
    """A rule fires when all required key/value pairs exist in the fact set."""

    name: str
    conditions: tuple[tuple[str, Any], ...]
    conclusion: tuple[str, Any]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("rule name must not be empty")
        if not self.conditions:
            raise ValueError("a rule must contain at least one condition")


class RuleEngine:
    """Apply deterministic rules and retain an ordered explanation trace."""

    def __init__(self, rules: Iterable[Rule] = ()) -> None:
        self.rules = tuple(rules)
        names = [rule.name for rule in self.rules]
        if len(names) != len(set(names)):
            raise ValueError("rule names must be unique")

    def infer_with_trace(self, initial_facts: dict[str, Any]) -> InferenceResult:
        """Infer facts and record the premises/conclusion of every rule firing."""
        facts = dict(initial_facts)
        trace: list[InferenceRecord] = []
        max_rounds = max(1, len(self.rules) * (len(facts) + 1))

        for _ in range(max_rounds):
            changed = False
            for rule in self.rules:
                if all(
                    key in facts and facts[key] == value
                    for key, value in rule.conditions
                ):
                    key, value = rule.conclusion
                    if key not in facts:
                        facts[key] = value
                        trace.append(
                            InferenceRecord(
                                sequence=len(trace) + 1,
                                rule_name=rule.name,
                                premises=tuple(rule.conditions),
                                conclusion_key=key,
                                conclusion_value=value,
                            )
                        )
                        changed = True
            if not changed:
                break

        return InferenceResult(facts=facts, trace=tuple(trace))

    def infer(self, initial_facts: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
        """Backward-compatible API returning facts and fired rule names."""
        result = self.infer_with_trace(initial_facts)
        return result.facts, result.fired_rules
