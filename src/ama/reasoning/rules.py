"""A minimal, explainable forward-chaining rule engine.

Rules use explicit key/value facts. No eval, dynamic code execution, or LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


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
    """Apply a finite set of deterministic rules until no new facts are inferred."""

    def __init__(self, rules: Iterable[Rule] = ()) -> None:
        self.rules = tuple(rules)
        names = [rule.name for rule in self.rules]
        if len(names) != len(set(names)):
            raise ValueError("rule names must be unique")

    def infer(self, initial_facts: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
        """Return a new fact mapping and the ordered names of rules that fired."""
        facts = dict(initial_facts)
        fired: list[str] = []
        max_rounds = max(1, len(self.rules) * (len(facts) + 1))

        for _ in range(max_rounds):
            changed = False
            for rule in self.rules:
                if all(facts.get(key, object()) == value for key, value in rule.conditions):
                    key, value = rule.conclusion
                    if key not in facts:
                        facts[key] = value
                        fired.append(rule.name)
                        changed = True
            if not changed:
                break

        return facts, tuple(fired)
