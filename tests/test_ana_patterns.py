import pytest

from ama.ana.patterns import (
    PatternDiscoveryParameters,
    PatternDiscoveryState,
    PatternPrototype,
    assign_pattern,
)


def params(**kwargs):
    values = dict(feature_size=1, max_prototypes=2, squared_distance_threshold=0.2)
    values.update(kwargs)
    return PatternDiscoveryParameters(**values)


def test_pattern_discovery_creates_and_updates_centroids():
    p = params()
    state = PatternDiscoveryState()
    first = assign_pattern(state, (0.0,), p)
    second = assign_pattern(first.state, (0.1,), p)
    assert first.created is True
    assert second.created is False
    assert second.prototype_id == 0
    assert second.state.prototypes[0].centroid == pytest.approx((0.05,))
    assert second.state.prototypes[0].count == 2
    assert state.prototypes == ()


def test_pattern_discovery_creates_new_cluster_until_capacity():
    p = params()
    first = assign_pattern(PatternDiscoveryState(), (0.0,), p)
    second = assign_pattern(first.state, (2.0,), p)
    third = assign_pattern(second.state, (10.0,), p)
    assert second.created is True
    assert third.created is False
    assert len(third.state.prototypes) == 2
    assert third.prototype_id == 1


def test_pattern_ties_choose_lowest_prototype_id():
    p = params(squared_distance_threshold=10.0)
    state = PatternDiscoveryState(
        prototypes=(
            PatternPrototype(0, (0.0,), 1),
            PatternPrototype(1, (2.0,), 1),
        ),
        next_id=2,
    )
    result = assign_pattern(state, (1.0,), p)
    assert result.prototype_id == 0


def test_pattern_dimensions_and_invalid_capacity_are_rejected():
    with pytest.raises(ValueError, match="positive"):
        PatternDiscoveryParameters(feature_size=1, max_prototypes=0, squared_distance_threshold=1.0)
    with pytest.raises(ValueError, match="length"):
        assign_pattern(PatternDiscoveryState(), (1.0, 2.0), params())



def test_pattern_discovery_separates_two_synthetic_groups():
    p = params(squared_distance_threshold=0.3)
    state = PatternDiscoveryState()
    assignments = []
    for value in (0.0, 0.1, 5.0, 5.1):
        result = assign_pattern(state, (value,), p)
        state = result.state
        assignments.append(result.prototype_id)

    assert assignments[0] == assignments[1]
    assert assignments[2] == assignments[3]
    assert assignments[0] != assignments[2]
    assert len(state.prototypes) == 2


def test_pattern_squared_distance_threshold_must_be_finite():
    with pytest.raises(ValueError, match="squared_distance_threshold"):
        params(squared_distance_threshold=10**400)


def test_pattern_uses_configured_squared_distance_threshold_directly():
    p = PatternDiscoveryParameters(
        feature_size=2, max_prototypes=2, squared_distance_threshold=0.2
    )
    first = assign_pattern(PatternDiscoveryState(), (0.0, 0.0), p)
    second = assign_pattern(first.state, (0.3, 0.1), p)
    assert second.created is False
    assert second.prototype_id == first.prototype_id
    assert second.distance_squared == pytest.approx(0.1)
