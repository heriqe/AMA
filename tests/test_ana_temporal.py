import math

import pytest

from ama.ana.temporal import (
    MultiScaleMemoryParameters,
    MultiScaleMemoryState,
    step_multiscale_memory,
)


def params(**kwargs):
    values = {
        "scale_ids": ("fast", "slow"),
        "retention": (0.0, 0.8),
        "context_weights": (1.0, 1.0),
    }
    values.update(kwargs)
    return MultiScaleMemoryParameters(**values)


def test_initial_state_has_zero_trace_for_each_scale():
    p = params()
    state = MultiScaleMemoryState.initial(p, signal_size=2)

    assert state.traces == ((0.0, 0.0), (0.0, 0.0))


def test_zero_retention_tracks_current_signal_immediately():
    p = params(retention=(0.0, 0.8))
    state = MultiScaleMemoryState.initial(p, 1)

    result = step_multiscale_memory(state, (0.75,), p)

    assert result.state.traces[0] == pytest.approx((0.75,))


def test_higher_retention_preserves_more_of_previous_trace():
    p = params(retention=(0.2, 0.8))
    state = MultiScaleMemoryState(
        traces=((1.0,), (1.0,))
    )

    result = step_multiscale_memory(state, (0.0,), p)

    assert result.state.traces[0][0] == pytest.approx(0.8)
    assert result.state.traces[1][0] == pytest.approx(0.2)


def test_context_is_normalized_weighted_sum_of_updated_traces():
    p = params(retention=(0.0, 0.5), context_weights=(1.0, 3.0))
    state = MultiScaleMemoryState(traces=((0.0,), (0.0,)))

    result = step_multiscale_memory(state, (1.0,), p)

    assert result.context == pytest.approx((0.625,))


def test_context_supports_multiple_dimensions():
    p = params()
    state = MultiScaleMemoryState.initial(p, 2)

    result = step_multiscale_memory(state, (0.5, -0.25), p)

    assert result.context == pytest.approx((0.3, -0.15))


def test_invalid_number_of_scales_is_rejected():
    with pytest.raises(ValueError, match="at least two"):
        params(scale_ids=("only",), retention=(0.5,), context_weights=(1.0,))


def test_retention_must_increase_from_fast_to_slow():
    with pytest.raises(ValueError, match="increase"):
        params(retention=(0.8, 0.2))


def test_invalid_weights_are_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        params(context_weights=(1.0, -1.0))
    with pytest.raises(ValueError, match="positive"):
        params(context_weights=(0.0, 0.0))


def test_non_finite_signal_is_rejected():
    p = params()
    state = MultiScaleMemoryState.initial(p, 1)

    with pytest.raises(ValueError, match="finite"):
        step_multiscale_memory(state, (math.inf,), p)


def test_state_dimension_is_validated():
    p = params()
    state = MultiScaleMemoryState(traces=((0.0,), (0.0, 0.0)))

    with pytest.raises(ValueError, match="length"):
        step_multiscale_memory(state, (1.0,), p)


def test_previous_state_is_not_mutated():
    p = params()
    state = MultiScaleMemoryState.initial(p, 1)
    snapshot = state

    step_multiscale_memory(state, (1.0,), p)

    assert state == snapshot


def test_same_inputs_are_deterministic():
    p = params()
    state = MultiScaleMemoryState.initial(p, 1)

    left = step_multiscale_memory(state, (0.3,), p)
    right = step_multiscale_memory(state, (0.3,), p)

    assert left == right
