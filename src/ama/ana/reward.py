"""Reward-modulated linear action preferences for ANA v0.4."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Matrix, Vector, _as_vector


@dataclass(frozen=True, slots=True)
class RewardLearningParameters:
    """Fixed dimensions, learning rates and numerical safety limits."""

    action_count: int
    feature_size: int
    learning_rate: float
    baseline_rate: float
    eligibility_decay: float
    max_abs_weight: float = 1_000_000.0
    max_abs_eligibility: float = 1_000_000.0

    def __post_init__(self) -> None:
        if isinstance(self.action_count, bool) or not isinstance(self.action_count, int) or self.action_count < 1:
            raise ValueError("action_count must be a positive integer")
        if isinstance(self.feature_size, bool) or not isinstance(self.feature_size, int) or self.feature_size < 1:
            raise ValueError("feature_size must be a positive integer")
        for name, value, lower, upper, inclusive_lower in (
            ("learning_rate", self.learning_rate, 0.0, math.inf, False),
            ("baseline_rate", self.baseline_rate, 0.0, 1.0, False),
            ("eligibility_decay", self.eligibility_decay, 0.0, 1.0, True),
            ("max_abs_weight", self.max_abs_weight, 0.0, math.inf, False),
            ("max_abs_eligibility", self.max_abs_eligibility, 0.0, math.inf, False),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            if (value < lower if inclusive_lower else value <= lower) or value > upper:
                raise ValueError(f"{name} is outside its valid range")


@dataclass(frozen=True, slots=True)
class RewardLearningState:
    """Immutable action weights, eligibility traces and scalar baseline."""

    weights: Matrix
    eligibility: Matrix
    baseline: float = 0.0

    @classmethod
    def initial(cls, parameters: RewardLearningParameters) -> "RewardLearningState":
        zeros = tuple((0.0,) * parameters.feature_size for _ in range(parameters.action_count))
        return cls(weights=zeros, eligibility=zeros, baseline=0.0)

    def __post_init__(self) -> None:
        if isinstance(self.baseline, bool) or not isinstance(self.baseline, (int, float)) or not math.isfinite(self.baseline):
            raise ValueError("baseline must be finite")
        if not self.weights or len(self.weights) != len(self.eligibility):
            raise ValueError("weights and eligibility must have matching action rows")
        if any(len(row) != len(self.weights[0]) for row in self.weights):
            raise ValueError("weights must be rectangular")
        if any(len(row) != len(self.weights[0]) for row in self.eligibility):
            raise ValueError("eligibility must match weight dimensions")
        for matrix_name, matrix in (("weights", self.weights), ("eligibility", self.eligibility)):
            for row in matrix:
                for value in row:
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                        raise ValueError(f"{matrix_name} must contain finite numeric values")


def action_scores(state: RewardLearningState, features: Vector, parameters: RewardLearningParameters) -> Vector:
    """Calculate one score per action."""
    _validate_state(state, parameters)
    x = _as_vector(features, "features", parameters.feature_size)
    scores = tuple(math.fsum(w * v for w, v in zip(row, x)) for row in state.weights)
    return _as_vector(scores, "action_scores", parameters.action_count)


def select_action(state: RewardLearningState, features: Vector, parameters: RewardLearningParameters) -> int:
    """Select the highest-scoring action; ties go to the lowest index."""
    scores = action_scores(state, features, parameters)
    return max(range(len(scores)), key=lambda index: (scores[index], -index))


def update_reward(
    state: RewardLearningState,
    features: Vector,
    action: int,
    reward: float,
    parameters: RewardLearningParameters,
) -> RewardLearningState:
    """Apply reward-modulated eligibility updates after caller-supplied feedback."""
    _validate_state(state, parameters)
    if isinstance(action, bool) or not isinstance(action, int) or not 0 <= action < parameters.action_count:
        raise ValueError("action index is outside the configured range")
    if isinstance(reward, bool) or not isinstance(reward, (int, float)) or not math.isfinite(reward):
        raise ValueError("reward must be finite")
    x = _as_vector(features, "features", parameters.feature_size)
    eligibility = [
        [parameters.eligibility_decay * value for value in row]
        for row in state.eligibility
    ]
    eligibility[action] = [
        old + current for old, current in zip(eligibility[action], x)
    ]
    delta = float(reward) - state.baseline
    weights = tuple(
        tuple(
            weight + parameters.learning_rate * delta * trace
            for weight, trace in zip(weight_row, trace_row)
        )
        for weight_row, trace_row in zip(state.weights, eligibility)
    )
    eligibility_tuple = tuple(tuple(row) for row in eligibility)
    if any(abs(value) > parameters.max_abs_weight or not math.isfinite(value) for row in weights for value in row):
        raise ValueError("updated weight magnitude exceeds configured limit")
    if any(abs(value) > parameters.max_abs_eligibility or not math.isfinite(value) for row in eligibility_tuple for value in row):
        raise ValueError("eligibility magnitude exceeds configured limit")
    baseline = state.baseline + parameters.baseline_rate * delta
    if not math.isfinite(baseline):
        raise ValueError("updated baseline must be finite")
    return RewardLearningState(weights=weights, eligibility=eligibility_tuple, baseline=baseline)


def _validate_state(state: RewardLearningState, parameters: RewardLearningParameters) -> None:
    expected = (parameters.action_count, parameters.feature_size)
    if len(state.weights) != expected[0] or len(state.eligibility) != expected[0]:
        raise ValueError("state action count does not match parameters")
    if any(len(row) != expected[1] for row in state.weights + state.eligibility):
        raise ValueError("state feature dimensions do not match parameters")
    if any(abs(value) > parameters.max_abs_weight for row in state.weights for value in row):
        raise ValueError("weight magnitude exceeds configured limit")
    if any(abs(value) > parameters.max_abs_eligibility for row in state.eligibility for value in row):
        raise ValueError("eligibility magnitude exceeds configured limit")
