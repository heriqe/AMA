from ama.reasoning.models import InferenceRecord
from ama.reasoning.rules import Rule, RuleEngine


def test_inference_trace_records_premises_and_conclusion():
    engine = RuleEngine(
        [
            Rule(
                name="eligible_market",
                conditions=(("country", "BR"), ("legal", True)),
                conclusion=("market_eligible", True),
            )
        ]
    )

    result = engine.infer_with_trace({"country": "BR", "legal": True})

    assert result.facts["market_eligible"] is True
    assert result.fired_rules == ("eligible_market",)
    assert result.trace == (
        InferenceRecord(
            sequence=1,
            rule_name="eligible_market",
            premises=(("country", "BR"), ("legal", True)),
            conclusion_key="market_eligible",
            conclusion_value=True,
        ),
    )


def test_inference_trace_supports_chained_rules():
    engine = RuleEngine(
        [
            Rule("first", (("a", 1),), ("b", 2)),
            Rule("second", (("b", 2),), ("c", 3)),
        ]
    )

    result = engine.infer_with_trace({"a": 1})

    assert result.facts == {"a": 1, "b": 2, "c": 3}
    assert result.fired_rules == ("first", "second")
    assert result.trace[1].premises == (("b", 2),)


def test_existing_infer_api_remains_compatible():
    engine = RuleEngine([Rule("derive", (("a", 1),), ("b", 2))])

    facts, fired = engine.infer({"a": 1})

    assert facts == {"a": 1, "b": 2}
    assert fired == ("derive",)
