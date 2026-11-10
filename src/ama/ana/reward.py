"""Reward-modulated linear action preferences for ANA v0.4."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Matrix, Vector, _as_vector


def _finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


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
        if not _finite_number(self.learning_rate) or self.learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")
        if not _finite_number(self.baseline_rate) or not 0 < self.baseline_rate <= 1:
            raise ValueError("baseline_rate must be finite and in (0, 1]")
        if not _finite_number(self.eligibility_decay) or not 0 <= self.eligibility_decay < 1:
            raise ValueError("eligibility_decay must be finite and in [0, 1)")
        if not _finite_number(self.max_abs_weight) or self.max_abs_weight <= 0:
            raise ValueError("max_abs_weight must be finite and positive")
        if not _finite_number(self.max_abs_eligibility) or self.max_abs_eligibility <= 0:
            raise ValueError("max_abs_eligibility must be finite and positive")


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
        if not _finite_number(self.baseline):
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
                    if not _finite_number(value):
                        raise ValueError(f"{matrix_name} must contain finite numeric values")


def action_scores(
    state: RewardLearningState,
    features: Vector,
    parameters: RewardLearningParameters,
) -> Vector:
    """Calculate one score per action."""
    _validate_state(state, parameters)
    x = _as_vector(features, "features", parameters.feature_size)
    scores = tuple(
        math.fsum(weight * value for weight, value in zip(row, x))
        for row in state.weights
    )
    return _as_vector(scores, "action_scores", parameters.action_count)


def select_action(
    state: RewardLearningState,
    features: Vector,
    parameters: RewardLearningParameters,
) -> int:
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
    if not _finite_number(reward):
        raise ValueError("reward must be finite")
    x = _as_vector(features, "features", parameters.feature_size)

    eligibility = [
        [parameters.eligibility_decay * value for value in row]
        for row in state.eligibility
    ]
    eligibility[action] = [
        previous + current
        for previous, current in zip(eligibility[action], x)
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

    if any(
        not math.isfinite(value) or abs(value) > parameters.max_abs_weight
        for row in weights for value in row
    ):
        raise ValueError("updated weight magnitude exceeds configured limit")
    if any(
        not math.isfinite(value) or abs(value) > parameters.max_abs_eligibility
        for row in eligibility_tuple for value in row
    ):
        raise ValueError("eligibility magnitude exceeds configured limit")

    baseline = state.baseline + parameters.baseline_rate * delta
    if not math.isfinite(baseline):
        raise ValueError("updated baseline must be finite")
    return RewardLearningState(
        weights=weights,
        eligibility=eligibility_tuple,
        baseline=baseline,
    )


def _validate_state(
    state: RewardLearningState,
    parameters: RewardLearningParameters,
) -> None:
    if len(state.weights) != parameters.action_count or len(state.eligibility) != parameters.action_count:
        raise ValueError("state action count does not match parameters")
    if any(
        len(row) != parameters.feature_size
        for row in state.weights + state.eligibility
    ):
        raise ValueError("state feature dimensions do not match parameters")
    if any(
        abs(value) > parameters.max_abs_weight
        for row in state.weights for value in row
    ):
        raise ValueError("weight magnitude exceeds configured limit")
    if any(
        abs(value) > parameters.max_abs_eligibility
        for row in state.eligibility for value in row
    ):
        raise ValueError("eligibility magnitude exceeds configured limit")
