import pytest

from ama.knowledge import Fact, SQLiteKnowledgeRepository


def test_fact_round_trips_with_provenance_and_confidence(tmp_path):
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.sqlite3")
    fact = Fact(
        predicate="market",
        value={"country": "BR"},
        source="manual-research",
        confidence=0.85,
    )

    repository.add(fact)
    restored = repository.get(fact.fact_id)

    assert restored == fact
    assert repository.find("market") == [fact]


def test_fact_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="confidence"):
        Fact(predicate="claim", value=True, source="test", confidence=1.5)


def test_fact_rejects_non_json_value():
    with pytest.raises(ValueError, match="JSON serializable"):
        Fact(predicate="claim", value=object(), source="test")
