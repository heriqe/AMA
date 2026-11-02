"""Bounded learning rules for the ANA v0.4 experimental scalar readout."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Vector, _as_vector


@dataclass(frozen=True, slots=True)
class LearningParameters:
    """Fixed learning rates and safety bounds for one adaptive readout."""

    learning_rate: float = 0.01
    eligibility_decay: float = 0.8
    baseline_rate: float = 0.05
    max_abs_weight: float = 5.0
    max_abs_update: float = 0.1
    max_abs_signal: float = 10.0

    def __post_init__(self) -> None:
        for name in (
            "learning_rate",
            "eligibility_decay",
            "baseline_rate",
            "max_abs_weight",
            "max_abs_update",
            "max_abs_signal",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")
        if not 0.0 <= self.eligibility_decay < 1.0:
            raise ValueError("eligibility_decay must satisfy 0 <= value < 1")
        if not 0.0 < self.baseline_rate <= 1.0:
            raise ValueError("baseline_rate must satisfy 0 < value <= 1")
        for name in ("max_abs_weight", "max_abs_update", "max_abs_signal"):
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} must be positive")


@dataclass(frozen=True, slots=True)
class LearningState:
    """Immutable weights, reward baseline and eligibility trace."""

    weights: Vector
    reward_baseline: float
    eligibility: Vector

    @classmethod
    def initial(cls, weights: Vector) -> "LearningState":
        checked = _as_vector(weights, "weights", len(weights))
        if not checked:
            raise ValueError("weights must not be empty")
        return cls(
            weights=checked,
            reward_baseline=0.0,
            eligibility=(0.0,) * len(checked),
        )


@dataclass(frozen=True, slots=True)
class LearningResult:
    """One learning transition; prediction and error refer to pre-update weights."""

    state: LearningState
    prediction: float
    error: float
    update: Vector


def _validate_state(
    state: LearningState, features: Vector, parameters: LearningParameters
) -> tuple[Vector, Vector]:
    if len(state.weights) == 0:
        raise ValueError("state weights must not be empty")
    checked_features = _as_vector(features, "features", len(state.weights))
    checked_weights = _as_vector(state.weights, "state.weights", len(state.weights))
    checked_eligibility = _as_vector(
        state.eligibility, "state.eligibility", len(state.weights)
    )
    if isinstance(state.reward_baseline, bool) or not isinstance(
        state.reward_baseline, (int, float)
    ):
        raise ValueError("reward_baseline must be numeric")
    if not math.isfinite(state.reward_baseline):
        raise ValueError("reward_baseline must be finite")
    if any(abs(value) > parameters.max_abs_weight for value in checked_weights):
        raise ValueError("state weight exceeds max_abs_weight")
    return checked_weights, checked_features


def _bounded_update(
    weights: Vector,
    gradient: Vector,
    parameters: LearningParameters,
) -> tuple[Vector, Vector]:
    updates = tuple(
        max(
            -parameters.max_abs_update,
            min(parameters.max_abs_update, parameters.learning_rate * value),
        )
        for value in gradient
    )
    next_weights = tuple(
        max(
            -parameters.max_abs_weight,
            min(parameters.max_abs_weight, weight + delta),
        )
        for weight, delta in zip(weights, updates)
    )
    actual_updates = tuple(
        new - old for old, new in zip(weights, next_weights)
    )
    return next_weights, actual_updates


def _validate_signal(value: float, name: str, parameters: LearningParameters) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if abs(result) > parameters.max_abs_signal:
        raise ValueError(f"{name} exceeds max_abs_signal")
    return result


def supervised_step(
    state: LearningState,
    features: Vector,
    target: float,
    parameters: LearningParameters,
) -> LearningResult:
    """Apply a bounded least-mean-squares update toward an explicit target."""
    weights, inputs = _validate_state(state, features, parameters)
    expected = _validate_signal(target, "target", parameters)
    prediction = sum(weight * value for weight, value in zip(weights, inputs))
    error = expected - prediction
    next_weights, update = _bounded_update(
        weights, tuple(error * value for value in inputs), parameters
    )
    return LearningResult(
        state=LearningState(next_weights, state.reward_baseline, state.eligibility),
        prediction=prediction,
        error=error,
        update=update,
    )


def autonomous_step(
    state: LearningState,
    features: Vector,
    next_observation: float,
    parameters: LearningParameters,
) -> LearningResult:
    """Learn a one-step prediction target supplied from the observed data stream.

    This is self-supervised prediction, not unsupervised discovery of arbitrary
    semantic structure. The caller provides the next scalar observation.
    """
    return supervised_step(state, features, next_observation, parameters)


def reward_step(
    state: LearningState,
    features: Vector,
    reward: float,
    parameters: LearningParameters,
) -> LearningResult:
    """Apply reward-modulated eligibility updates using a moving reward baseline."""
    weights, inputs = _validate_state(state, features, parameters)
    checked_eligibility = _as_vector(
        state.eligibility, "state.eligibility", len(weights)
    )
    observed_reward = _validate_signal(reward, "reward", parameters)
    prediction = sum(weight * value for weight, value in zip(weights, inputs))
    eligibility = tuple(
        parameters.eligibility_decay * old + current
        for old, current in zip(checked_eligibility, inputs)
    )
    advantage = observed_reward - float(state.reward_baseline)
    next_weights, update = _bounded_update(
        weights, tuple(advantage * value for value in eligibility), parameters
    )
    baseline = (
        float(state.reward_baseline)
        + parameters.baseline_rate
        * (observed_reward - float(state.reward_baseline))
    )
    return LearningResult(
        state=LearningState(next_weights, baseline, eligibility),
        prediction=prediction,
        error=advantage,
        update=update,
    )
