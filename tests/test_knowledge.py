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


def test_in_memory_repository_keeps_data_between_operations():
    repository = SQLiteKnowledgeRepository(":memory:")
    fact = Fact(predicate="status", value="active", source="test")

    repository.add(fact)

    assert repository.get(fact.fact_id) == fact
    repository.close()


@pytest.mark.parametrize("confidence", [-0.1, 1.1, float("nan"), True, "high"])
def test_fact_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        Fact(predicate="claim", value=True, source="test", confidence=confidence)


def test_fact_rejects_non_json_value():
    with pytest.raises(ValueError, match="JSON serializable"):
        Fact(predicate="claim", value=object(), source="test")


def test_fact_rejects_invalid_predicate_type():
    with pytest.raises(ValueError, match="predicate"):
        Fact(predicate=None, value=True, source="test")
