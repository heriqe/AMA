from ama.reasoning.rules import Rule, RuleEngine


def test_rule_engine_infers_conclusion_and_explanation():
    engine = RuleEngine(
        [
            Rule(
                name="eligible_when_validated",
                conditions=(("validated", True), ("legal", True)),
                conclusion=("eligible_for_review", True),
            )
        ]
    )

    facts, fired = engine.infer({"validated": True, "legal": True})

    assert facts["eligible_for_review"] is True
    assert fired == ("eligible_when_validated",)


def test_rule_engine_does_not_infer_when_condition_is_missing():
    engine = RuleEngine(
        [
            Rule(
                name="requires_budget",
                conditions=(("budget_approved", True),),
                conclusion=("execution_allowed", True),
            )
        ]
    )

    facts, fired = engine.infer({})

    assert "execution_allowed" not in facts
    assert fired == ()
