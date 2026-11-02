import math

import pytest

from ama.ana.learning import (
    LearningParameters,
    LearningState,
    autonomous_step,
    reward_step,
    supervised_step,
)


def parameters(**kwargs):
    values = {
        "learning_rate": 0.1,
        "eligibility_decay": 0.5,
        "baseline_rate": 0.25,
        "max_abs_weight": 1.0,
        "max_abs_update": 0.2,
        "max_abs_signal": 5.0,
    }
    values.update(kwargs)
    return LearningParameters(**values)


def test_supervised_zero_error_does_not_change_weights():
    p = parameters()
    state = LearningState.initial((0.5, 0.25))
    result = supervised_step(state, (1.0, 2.0), 1.0, p)
    assert result.prediction == pytest.approx(1.0)
    assert result.error == pytest.approx(0.0)
    assert result.state.weights == state.weights


def test_supervised_update_moves_toward_target():
    p = parameters()
    state = LearningState.initial((0.0, 0.0))
    result = supervised_step(state, (1.0, 2.0), 2.0, p)
    assert result.state.weights == pytest.approx((0.2, 0.2))
    assert result.error == pytest.approx(2.0)


def test_supervised_update_is_clipped_per_weight():
    p = parameters(max_abs_update=0.05)
    state = LearningState.initial((0.0,))
    result = supervised_step(state, (1.0,), 5.0, p)
    assert result.update == pytest.approx((0.05,))


def test_weight_bound_is_enforced():
    p = parameters(max_abs_weight=0.5)
    state = LearningState.initial((0.49,))
    result = supervised_step(state, (1.0,), 5.0, p)
    assert result.state.weights[0] == pytest.approx(0.5)
    assert abs(result.state.weights[0]) <= p.max_abs_weight


def test_autonomous_prediction_learns_next_observation():
    p = parameters()
    state = LearningState.initial((0.0,))
    result = autonomous_step(state, (1.0,), 1.0, p)
    assert result.prediction == pytest.approx(0.0)
    assert result.state.weights == pytest.approx((0.1,))


def test_reward_step_updates_eligibility_and_baseline():
    p = parameters()
    state = LearningState.initial((0.0,))
    result = reward_step(state, (1.0,), 2.0, p)
    assert result.state.eligibility == pytest.approx((1.0,))
    assert result.state.reward_baseline == pytest.approx(0.5)
    assert result.state.weights == pytest.approx((0.2,))


def test_reward_uses_baseline_adjusted_advantage():
    p = parameters()
    state = LearningState(
        weights=(0.0,), reward_baseline=1.0, eligibility=(0.0,)
    )
    result = reward_step(state, (1.0,), 1.0, p)
    assert result.error == pytest.approx(0.0)
    assert result.state.weights == pytest.approx((0.0,))


def test_reward_eligibility_accumulates_with_decay():
    p = parameters()
    state = LearningState(
        weights=(0.0,), reward_baseline=0.0, eligibility=(2.0,)
    )
    result = reward_step(state, (1.0,), 1.0, p)
    assert result.state.eligibility == pytest.approx((2.0,))


def test_weight_update_is_deterministic():
    p = parameters()
    state = LearningState.initial((0.1, -0.1))
    left = supervised_step(state, (0.5, 0.25), 0.8, p)
    right = supervised_step(state, (0.5, 0.25), 0.8, p)
    assert left == right


def test_previous_state_is_not_mutated():
    p = parameters()
    state = LearningState.initial((0.0,))
    snapshot = state
    supervised_step(state, (1.0,), 1.0, p)
    assert state == snapshot


def test_non_finite_target_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        supervised_step(
            LearningState.initial((0.0,)), (1.0,), math.inf, parameters()
        )


def test_signal_outside_configured_limit_is_rejected():
    with pytest.raises(ValueError, match="max_abs_signal"):
        reward_step(
            LearningState.initial((0.0,)), (1.0,), 6.0, parameters()
        )


def test_feature_dimensions_are_validated():
    with pytest.raises(ValueError, match="length"):
        supervised_step(
            LearningState.initial((0.0, 0.0)), (1.0,), 1.0, parameters()
        )


def test_invalid_learning_rates_are_rejected():
    with pytest.raises(ValueError, match="learning_rate"):
        parameters(learning_rate=0.0)
    with pytest.raises(ValueError, match="eligibility_decay"):
        parameters(eligibility_decay=1.0)


def test_invalid_weight_state_is_rejected():
    with pytest.raises(ValueError, match="max_abs_weight"):
        supervised_step(
            LearningState.initial((2.0,)), (1.0,), 1.0, parameters()
        )


def test_features_outside_signal_limit_are_rejected():
    with pytest.raises(ValueError, match="feature exceeds"):
        supervised_step(
            LearningState.initial((0.0,)), (6.0,), 1.0, parameters()
        )


def test_invalid_eligibility_state_is_rejected_by_all_rules():
    state = LearningState(weights=(0.0,), reward_baseline=0.0, eligibility=())
    with pytest.raises(ValueError, match="state.eligibility"):
        supervised_step(state, (1.0,), 1.0, parameters())


def test_reward_eligibility_trace_is_bounded():
    p = parameters(max_abs_signal=2.0)
    state = LearningState(weights=(0.0,), reward_baseline=0.0, eligibility=(2.0,))
    result = reward_step(state, (2.0,), 1.0, p)
    assert result.state.eligibility == pytest.approx((2.0,))
