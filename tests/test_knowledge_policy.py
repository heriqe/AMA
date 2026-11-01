from datetime import datetime, timezone

import pytest

from ama.knowledge.models import Fact
from ama.knowledge.policy import KnowledgePolicy


NOW = datetime(2026, 11, 1, 19, 0, tzinfo=timezone.utc)


def test_policy_accepts_single_eligible_fact():
    fact = Fact(predicate="market", value="Brazil", source="research", confidence=0.9)
    result = KnowledgePolicy().assess([fact], now=NOW)

    assert result.as_mapping() == {"market": "Brazil"}
    assert result.assessments[0].status == "accepted"
    assert result.resolved[0].source_fact_ids == (fact.fact_id,)


def test_policy_does_not_resolve_conflicting_eligible_values():
    first = Fact(predicate="price", value=10, source="source-a", confidence=0.9)
    second = Fact(predicate="price", value=12, source="source-b", confidence=0.8)

    result = KnowledgePolicy().assess([first, second], now=NOW)

    assert result.as_mapping() == {}
    assert [item.status for item in result.assessments] == ["conflict", "conflict"]


def test_policy_ignores_expired_and_low_confidence_facts():
    expired = Fact(
        predicate="status",
        value="old",
        source="archive",
        confidence=1.0,
        valid_until="2026-11-01T18:59:59+00:00",
    )
    weak = Fact(predicate="status", value="uncertain", source="unknown", confidence=0.2)
    current = Fact(predicate="status", value="active", source="verified", confidence=0.9)

    result = KnowledgePolicy(minimum_confidence=0.6).assess(
        [expired, weak, current], now=NOW
    )

    assert result.as_mapping() == {"status": "active"}
    assert [item.status for item in result.assessments] == [
        "expired",
        "low_confidence",
        "accepted",
    ]


def test_policy_accepts_multiple_sources_when_values_agree():
    facts = [
        Fact(predicate="currency", value="BRL", source="a", confidence=0.7),
        Fact(predicate="currency", value="BRL", source="b", confidence=0.9),
    ]

    result = KnowledgePolicy().assess(facts, now=NOW)

    assert result.as_mapping() == {"currency": "BRL"}
    assert len(result.resolved[0].source_fact_ids) == 2


def test_policy_validates_threshold():
    with pytest.raises(ValueError):
        KnowledgePolicy(minimum_confidence=1.1)
