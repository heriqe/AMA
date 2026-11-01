import pytest

from ama.perception import normalize_observation


def test_normalize_structured_observation():
    observation = normalize_observation(
        {
            "source": "market-scan",
            "facts": [
                {"predicate": "country", "value": "BR", "confidence": 0.9},
                {"predicate": "eligible", "value": True},
            ],
        }
    )

    assert observation.source == "market-scan"
    assert len(observation.facts) == 2
    assert observation.facts[0].source == "market-scan"
    assert observation.facts[0].confidence == 0.9
    assert observation.facts[1].confidence == 1.0


def test_normalizer_rejects_missing_fact_fields():
    with pytest.raises(ValueError, match="requires predicate and value"):
        normalize_observation({"source": "test", "facts": [{"predicate": "x"}]})
