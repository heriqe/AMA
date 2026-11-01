"""Deterministic, non-executing decision support under explicit constraints."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable


_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


def _money(value: Decimal | int | str, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name} must be Decimal, int, or decimal string")
    try:
        result = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a valid decimal amount") from error
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    if result < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return result


def _unit_interval(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{field_name} must be finite and between 0 and 1")
    return float(value)


def _currency(value: str) -> str:
    if not isinstance(value, str) or not _CURRENCY_PATTERN.fullmatch(value):
        raise ValueError("currency must be a three-letter uppercase code")
    return value


@dataclass(frozen=True, slots=True)
class DecisionBudget:
    """Available planning budget; this is a limit, not permission to spend."""

    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", _money(self.amount, "budget amount"))
        object.__setattr__(self, "currency", _currency(self.currency))


@dataclass(frozen=True, slots=True)
class Alternative:
    """A candidate with explicitly supplied estimates and evidence metadata."""

    alternative_id: str
    description: str
    projected_revenue: Decimal
    estimated_cost: Decimal
    risk_score: float
    evidence_confidence: float
    currency: str = "BRL"
    requires_human_approval: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.alternative_id, str) or not self.alternative_id.strip():
            raise ValueError("alternative_id must not be empty")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must not be empty")
        object.__setattr__(
            self, "projected_revenue", _money(self.projected_revenue, "projected_revenue")
        )
        object.__setattr__(
            self, "estimated_cost", _money(self.estimated_cost, "estimated_cost")
        )
        object.__setattr__(self, "risk_score", _unit_interval(self.risk_score, "risk_score"))
        object.__setattr__(
            self,
            "evidence_confidence",
            _unit_interval(self.evidence_confidence, "evidence_confidence"),
        )
        object.__setattr__(self, "currency", _currency(self.currency))
        if not isinstance(self.requires_human_approval, bool):
            raise ValueError("requires_human_approval must be boolean")


@dataclass(frozen=True, slots=True)
class DecisionPolicy:
    """Hard constraints and a transparent risk penalty for ranking candidates."""

    maximum_risk: float = 0.7
    minimum_evidence_confidence: float = 0.5
    risk_weight: float = 0.25
    minimum_net_value: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "maximum_risk", _unit_interval(self.maximum_risk, "maximum_risk")
        )
        object.__setattr__(
            self,
            "minimum_evidence_confidence",
            _unit_interval(
                self.minimum_evidence_confidence, "minimum_evidence_confidence"
            ),
        )
        object.__setattr__(self, "risk_weight", _unit_interval(self.risk_weight, "risk_weight"))
        object.__setattr__(
            self, "minimum_net_value", _money(self.minimum_net_value, "minimum_net_value")
        )


@dataclass(frozen=True, slots=True)
class AlternativeAssessment:
    """Auditable result for one candidate."""

    alternative_id: str
    status: str
    reason: str
    projected_net_value: Decimal
    normalized_score: float | None


@dataclass(frozen=True, slots=True)
class DecisionResult:
    """Ranked recommendation; it never executes or authorizes an action."""

    selected_alternative_id: str | None
    assessments: tuple[AlternativeAssessment, ...]
    abstained: bool
    rationale: str


class DecisionEngine:
    """Select a feasible candidate or abstain when constraints reject all."""

    def __init__(self, policy: DecisionPolicy | None = None) -> None:
        self.policy = policy or DecisionPolicy()

    def evaluate(
        self,
        alternatives: Iterable[Alternative],
        budget: DecisionBudget,
    ) -> DecisionResult:
        """Evaluate estimates deterministically without spending or side effects."""
        candidates = tuple(alternatives)
        ids = [item.alternative_id for item in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("alternative IDs must be unique")

        assessments: list[AlternativeAssessment] = []
        eligible: list[tuple[float, str]] = []

        for item in candidates:
            net_value = item.projected_revenue - item.estimated_cost
            status = "eligible"
            reason = "within constraints"
            score: float | None = None

            if item.currency != budget.currency:
                status, reason = "currency_mismatch", "candidate and budget currencies differ"
            elif item.estimated_cost > budget.amount:
                status, reason = "over_budget", "estimated cost exceeds available budget"
            elif item.risk_score > self.policy.maximum_risk:
                status, reason = "risk_too_high", "risk score exceeds policy maximum"
            elif item.evidence_confidence < self.policy.minimum_evidence_confidence:
                status, reason = (
                    "insufficient_evidence",
                    "evidence confidence is below policy threshold",
                )
            elif net_value < self.policy.minimum_net_value:
                status, reason = "negative_value", "projected net value is below policy minimum"
            elif item.requires_human_approval:
                status, reason = (
                    "approval_required",
                    "candidate requires explicit human approval before proceeding",
                )
            else:
                scale = max(budget.amount, Decimal("1"))
                score = float(net_value / scale) - (
                    self.policy.risk_weight * item.risk_score
                )
                eligible.append((score, item.alternative_id))

            assessments.append(
                AlternativeAssessment(
                    alternative_id=item.alternative_id,
                    status=status,
                    reason=reason,
                    projected_net_value=net_value,
                    normalized_score=score,
                )
            )

        if not eligible:
            return DecisionResult(
                selected_alternative_id=None,
                assessments=tuple(assessments),
                abstained=True,
                rationale="No candidate satisfies all decision constraints.",
            )

        # Stable tie-break: lexicographically smaller ID wins equal scores.
        eligible.sort(key=lambda item: (-item[0], item[1]))
        selected_id = eligible[0][1]
        return DecisionResult(
            selected_alternative_id=selected_id,
            assessments=tuple(assessments),
            abstained=False,
            rationale=(
                "Selected the highest risk-adjusted normalized score among "
                "candidates satisfying all hard constraints."
            ),
        )
