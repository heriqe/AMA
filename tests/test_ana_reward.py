import pytest

from ama.ana.reward import (
    RewardLearningParameters,
    RewardLearningState,
    action_scores,
    select_action,
    update_reward,
)


def params(**kwargs):
    values = dict(
        action_count=2,
        feature_size=1,
        learning_rate=0.1,
        baseline_rate=0.5,
        eligibility_decay=0.5,
    )
    values.update(kwargs)
    return RewardLearningParameters(**values)


def test_reward_update_changes_selected_action_preference_and_baseline():
    p = params()
    state = RewardLearningState.initial(p)
    updated = update_reward(state, (1.0,), 1, 1.0, p)
    assert updated.weights[1] == pytest.approx((0.1,))
    assert updated.baseline == pytest.approx(0.5)
    assert state.weights[1] == (0.0,)


def test_reward_eligibility_decays_and_carries_across_actions():
    p = params()
    state = RewardLearningState.initial(p)
    first = update_reward(state, (1.0,), 1, 1.0, p)
    second = update_reward(first, (1.0,), 0, 0.0, p)
    assert second.eligibility == pytest.approx(((1.0,), (0.5,)))
    assert second.weights[0] == pytest.approx((-0.05,))
    assert second.weights[1] == pytest.approx((0.075,))


def test_action_selection_is_deterministic_and_ties_choose_lowest_index():
    p = params()
    state = RewardLearningState.initial(p)
    assert action_scores(state, (1.0,), p) == (0.0, 0.0)
    assert select_action(state, (1.0,), p) == 0


def test_reward_invalid_action_reward_and_dimensions_are_rejected():
    p = params()
    state = RewardLearningState.initial(p)
    with pytest.raises(ValueError, match="action index"):
        update_reward(state, (1.0,), 2, 1.0, p)
    with pytest.raises(ValueError, match="finite"):
        update_reward(state, (1.0,), 0, float("nan"), p)
    with pytest.raises(ValueError, match="length"):
        action_scores(state, (1.0, 2.0), p)
