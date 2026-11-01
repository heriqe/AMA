from decimal import Decimal

import pytest

from ama.decision.engine import (
    Alternative,
    DecisionBudget,
    DecisionEngine,
    DecisionPolicy,
)


def candidate(
    alternative_id,
    *,
    revenue="1000",
    cost="200",
    risk=0.2,
    evidence=0.9,
    currency="BRL",
    approval=False,
):
    return Alternative(
        alternative_id=alternative_id,
        description=f"Candidate {alternative_id}",
        projected_revenue=Decimal(revenue),
        estimated_cost=Decimal(cost),
        risk_score=risk,
        evidence_confidence=evidence,
        currency=currency,
        requires_human_approval=approval,
    )


def test_selects_highest_risk_adjusted_score_within_budget():
    engine = DecisionEngine(DecisionPolicy(risk_weight=0.5))
    result = engine.evaluate(
        [
            candidate("steady", revenue="900", cost="200", risk=0.1),
            candidate("risky", revenue="1500", cost="200", risk=0.9),
        ],
        DecisionBudget(Decimal("500")),
    )

    assert result.selected_alternative_id == "steady"
    assert not result.abstained


def test_abstains_when_all_candidates_exceed_budget():
    result = DecisionEngine().evaluate(
        [candidate("too-expensive", cost="501")],
        DecisionBudget(Decimal("500")),
    )

    assert result.abstained
    assert result.selected_alternative_id is None
    assert result.assessments[0].status == "over_budget"


def test_rejects_currency_mismatch():
    result = DecisionEngine().evaluate(
        [candidate("usd", currency="USD")],
        DecisionBudget(Decimal("500"), "BRL"),
    )

    assert result.assessments[0].status == "currency_mismatch"
    assert result.abstained


def test_rejects_excessive_risk():
    engine = DecisionEngine(DecisionPolicy(maximum_risk=0.4))
    result = engine.evaluate(
        [candidate("risky", risk=0.5)],
        DecisionBudget(Decimal("500")),
    )

    assert result.assessments[0].status == "risk_too_high"
    assert result.abstained


def test_rejects_low_evidence_confidence():
    engine = DecisionEngine(DecisionPolicy(minimum_evidence_confidence=0.7))
    result = engine.evaluate(
        [candidate("weak-evidence", evidence=0.4)],
        DecisionBudget(Decimal("500")),
    )

    assert result.assessments[0].status == "insufficient_evidence"
    assert result.abstained


def test_rejects_negative_projected_net_value():
    result = DecisionEngine().evaluate(
        [candidate("loss", revenue="100", cost="200")],
        DecisionBudget(Decimal("500")),
    )

    assert result.assessments[0].status == "negative_value"
    assert result.assessments[0].projected_net_value == Decimal("-100")


def test_human_approval_candidate_is_not_automatically_selected():
    result = DecisionEngine().evaluate(
        [candidate("needs-approval", approval=True)],
        DecisionBudget(Decimal("500")),
    )

    assert result.assessments[0].status == "approval_required"
    assert result.abstained


def test_deterministic_tie_break_uses_candidate_id():
    result = DecisionEngine(DecisionPolicy(risk_weight=0.0)).evaluate(
        [candidate("zeta"), candidate("alpha")],
        DecisionBudget(Decimal("5000")),
    )

    assert result.selected_alternative_id == "alpha"


def test_duplicate_candidate_ids_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        DecisionEngine().evaluate(
            [candidate("same"), candidate("same")],
            DecisionBudget(Decimal("500")),
        )


def test_money_rejects_float_and_non_finite_values():
    with pytest.raises(ValueError, match="Decimal, int"):
        Alternative(
            alternative_id="float",
            description="Invalid float amount",
            projected_revenue=1.5,
            estimated_cost=Decimal("1"),
            risk_score=0.1,
            evidence_confidence=0.9,
        )
    with pytest.raises(ValueError, match="finite"):
        DecisionBudget(Decimal("Infinity"))


def test_decision_engine_has_no_execution_side_effects():
    budget = DecisionBudget(Decimal("500"))
    alternatives = [candidate("safe")]
    before = (budget, tuple(alternatives))

    DecisionEngine().evaluate(alternatives, budget)

    assert (budget, tuple(alternatives)) == before
