import math

import pytest

from ama.ana.network import Connection
from ama.ana.plasticity import (
    PlasticConnection,
    PlasticityParameters,
    PlasticityState,
    step_plasticity,
)


def params(**kwargs):
    values = {
        "learning_rate": 0.1,
        "weight_decay": 0.0,
        "max_abs_weight": 1.0,
        "activation_threshold": 0.5,
        "activation_steps": 2,
        "prune_threshold": 0.05,
        "prune_steps": 2,
        "max_abs_activity": 1.0,
        "initial_weight": 0.1,
    }
    values.update(kwargs)
    return PlasticityParameters(**values)


def test_active_connection_strengthens_with_positive_coactivation():
    state = PlasticityState.initial((("a", "b"),), (0.2,))
    result = step_plasticity(state, {"a": 1.0, "b": 1.0}, params())
    assert result.connections[0].weight == pytest.approx(0.3)
    assert result.connections[0].active


def test_active_connection_weakens_with_opposite_activity():
    state = PlasticityState.initial((("a", "b"),), (0.2,))
    result = step_plasticity(state, {"a": 1.0, "b": -1.0}, params())
    assert result.connections[0].weight == pytest.approx(0.1)


def test_weight_is_clipped_to_configured_bound():
    state = PlasticityState.initial((("a", "b"),), (0.95,))
    result = step_plasticity(state, {"a": 1.0, "b": 1.0}, params())
    assert result.connections[0].weight == 1.0


def test_inactive_candidate_activates_after_consecutive_coactivation():
    state = PlasticityState.initial((("a", "b"),))
    first = step_plasticity(state, {"a": 1.0, "b": 1.0}, params())
    assert not first.connections[0].active
    assert first.connections[0].activation_count == 1
    second = step_plasticity(first, {"a": 1.0, "b": 1.0}, params())
    assert second.connections[0].active
    assert second.connections[0].weight == pytest.approx(0.1)
    third = step_plasticity(second, {"a": 1.0, "b": 1.0}, params())
    assert third.connections[0].weight == pytest.approx(0.2)


def test_break_in_coactivation_resets_activation_counter():
    state = PlasticityState.initial((("a", "b"),))
    first = step_plasticity(state, {"a": 1.0, "b": 1.0}, params())
    second = step_plasticity(first, {"a": 0.0, "b": 1.0}, params())
    assert second.connections[0].activation_count == 0
    assert not second.connections[0].active


def test_weak_connection_is_pruned_after_consecutive_steps():
    state = PlasticityState.initial((("a", "b"),), (0.01,))
    p = params(learning_rate=0.001, prune_steps=2)
    first = step_plasticity(state, {"a": 0.0, "b": 0.0}, p)
    assert first.connections[0].active
    assert first.connections[0].prune_count == 1
    second = step_plasticity(first, {"a": 0.0, "b": 0.0}, p)
    assert not second.connections[0].active
    assert second.connections[0].weight == 0.0


def test_recovery_resets_pruning_counter():
    state = PlasticityState.initial((("a", "b"),), (0.01,))
    p = params(learning_rate=0.1, prune_steps=3)
    first = step_plasticity(state, {"a": 0.0, "b": 0.0}, p)
    assert first.connections[0].prune_count == 1
    second = step_plasticity(first, {"a": 1.0, "b": 1.0}, p)
    assert second.connections[0].prune_count == 0
    assert second.connections[0].weight > p.prune_threshold


def test_active_connections_convert_to_v02_edges_in_stable_order():
    state = PlasticityState.initial(
        (("a", "b"), ("b", "a"), ("c", "c")),
        (0.2, 0.0, -0.1),
    )
    assert state.active_connections() == (
        Connection("a", "b", 0.2),
        Connection("c", "c", -0.1),
    )


def test_self_connections_remain_compatible_with_v02_network_edges():
    state = PlasticityState.initial((("a", "a"),), (0.1,))
    assert state.active_connections() == (Connection("a", "a", 0.1),)


def test_previous_state_is_immutable_and_transition_is_deterministic():
    state = PlasticityState.initial((("a", "b"),), (0.2,))
    activities = {"a": 0.8, "b": 0.9}
    left = step_plasticity(state, activities, params())
    right = step_plasticity(state, activities, params())
    assert left == right
    assert state.connections[0].weight == 0.2


def test_initial_inputs_are_snapshotted():
    pairs = [["a", "b"]]
    weights = [0.2]
    state = PlasticityState.initial(pairs, weights)
    pairs[0][0] = "changed"
    weights[0] = 0.9
    assert state.connections[0].source == "a"
    assert state.connections[0].weight == 0.2


def test_state_snapshots_mutable_connection_collection():
    items = [PlasticConnection("a", "b", 0.2, True)]
    state = PlasticityState(items)
    items.clear()
    assert len(state.connections) == 1


def test_inactive_connections_must_have_zero_weight():
    with pytest.raises(ValueError, match="zero weight"):
        PlasticConnection("a", "b", 0.1, False)


def test_invalid_candidate_pairs_and_duplicates_are_rejected():
    with pytest.raises(ValueError, match="unique"):
        PlasticityState.initial((("a", "b"), ("a", "b")))
    with pytest.raises(ValueError, match="non-empty"):
        PlasticityState.initial((("", "b"),))
    with pytest.raises(ValueError, match="source and target"):
        PlasticityState.initial((("a",),))


def test_initial_weights_must_match_candidates_and_be_finite():
    with pytest.raises(ValueError, match="match"):
        PlasticityState.initial((("a", "b"),), (0.1, 0.2))
    with pytest.raises(ValueError, match="finite"):
        PlasticityState.initial((("a", "b"),), (math.inf,))


def test_missing_activity_for_candidate_endpoint_is_rejected():
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError, match="every candidate endpoint"):
        step_plasticity(state, {"a": 1.0}, params())


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True, 2.0])
def test_invalid_or_out_of_range_activity_is_rejected(value):
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError):
        step_plasticity(state, {"a": value, "b": 1.0}, params())


def test_activity_node_ids_must_be_non_empty():
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError, match="node IDs"):
        step_plasticity(state, {"": 0.0, "a": 1.0, "b": 1.0}, params())


def test_parameter_bounds_and_types_are_validated():
    with pytest.raises(ValueError, match="learning_rate"):
        params(learning_rate=0.0)
    with pytest.raises(ValueError, match="weight_decay"):
        params(weight_decay=1.1)
    with pytest.raises(ValueError, match="activation_steps"):
        params(activation_steps=True)
    with pytest.raises(ValueError, match="initial_weight"):
        params(initial_weight=0.0)
    with pytest.raises(ValueError, match="finite"):
        params(learning_rate=10**400)


def test_weight_update_overflow_is_rejected():
    state = PlasticityState.initial((("a", "b"),), (0.1,))
    p = params(learning_rate=1e308, max_abs_activity=1e154)
    with pytest.raises(ValueError, match="weight update overflowed"):
        step_plasticity(state, {"a": 1e154, "b": 1e154}, p)


def test_long_run_keeps_each_weight_finite_and_bounded():
    p = params(learning_rate=0.2, weight_decay=0.1, prune_threshold=0.0)
    state = PlasticityState.initial((("a", "b"),), (0.05,))
    for index in range(5_000):
        pre = 1.0 if index % 2 == 0 else -1.0
        state = step_plasticity(state, {"a": pre, "b": 1.0}, p)
        weight = state.connections[0].weight
        assert math.isfinite(weight)
        assert abs(weight) <= p.max_abs_weight
