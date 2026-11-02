import pytest

from ama.ana.network import Connection
from ama.ana.plasticity import (
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


def test_weight_is_bounded():
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


def test_break_in_coactivation_resets_activation_counter():
    state = PlasticityState.initial((("a", "b"),))
    first = step_plasticity(state, {"a": 1.0, "b": 1.0}, params())
    second = step_plasticity(first, {"a": 0.0, "b": 1.0}, params())
    assert second.connections[0].activation_count == 0
    assert not second.connections[0].active


def test_weak_connection_is_pruned_after_consecutive_steps():
    state = PlasticityState.initial((("a", "b"),), (0.01,))
    p = params(learning_rate=0.001, weight_decay=0.0)
    first = step_plasticity(state, {"a": 0.0, "b": 0.0}, p)
    assert first.connections[0].active
    assert first.connections[0].prune_count == 1
    second = step_plasticity(first, {"a": 0.0, "b": 0.0}, p)
    assert not second.connections[0].active
    assert second.connections[0].weight == 0.0


def test_stronger_weight_resets_pruning_counter():
    state = PlasticityState.initial((("a", "b"),), (0.01,))
    p = params(learning_rate=0.1, prune_steps=3)
    first = step_plasticity(state, {"a": 0.0, "b": 0.0}, p)
    second = step_plasticity(first, {"a": 1.0, "b": 1.0}, p)
    assert second.connections[0].prune_count == 0


def test_active_connections_convert_to_network_edges():
    state = PlasticityState.initial((("a", "b"), ("b", "a")), (0.2, 0.0))
    assert state.active_connections() == (Connection("a", "b", 0.2),)


def test_previous_state_is_immutable_and_step_is_deterministic():
    state = PlasticityState.initial((("a", "b"),), (0.2,))
    activity = {"a": 0.8, "b": 0.9}
    left = step_plasticity(state, activity, params())
    right = step_plasticity(state, activity, params())
    assert left == right
    assert state.connections[0].weight == 0.2


def test_candidate_pairs_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        PlasticityState.initial((("a", "b"), ("a", "b")))


def test_initial_weights_must_match_candidates():
    with pytest.raises(ValueError, match="match"):
        PlasticityState.initial((("a", "b"),), (0.1, 0.2))


def test_activity_for_all_endpoints_is_required():
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError, match="every candidate"):
        step_plasticity(state, {"a": 1.0}, params())


def test_invalid_activity_is_rejected():
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError, match="finite"):
        step_plasticity(state, {"a": float("inf"), "b": 1.0}, params())


def test_activity_bounds_are_enforced():
    state = PlasticityState.initial((("a", "b"),))
    with pytest.raises(ValueError, match="max_abs_activity"):
        step_plasticity(state, {"a": 2.0, "b": 1.0}, params())


def test_self_connections_are_rejected():
    with pytest.raises(ValueError, match="self-connections"):
        PlasticityState.initial((("a", "a"),))


def test_invalid_parameter_values_are_rejected():
    with pytest.raises(ValueError, match="activation_steps"):
        params(activation_steps=0)
    with pytest.raises(ValueError, match="weight_decay"):
        params(weight_decay=-0.1)


def test_explicit_empty_initial_weights_are_rejected():
    with pytest.raises(ValueError, match="match"):
        PlasticityState.initial((("a", "b"),), ())


def test_decay_must_not_exceed_one():
    with pytest.raises(ValueError, match="weight_decay"):
        params(weight_decay=1.1)


def test_activation_steps_must_be_integer_not_boolean():
    with pytest.raises(ValueError, match="positive integer"):
        params(activation_steps=True)


def test_zero_activation_threshold_is_rejected():
    with pytest.raises(ValueError, match="activation_threshold"):
        params(activation_threshold=0.0)
