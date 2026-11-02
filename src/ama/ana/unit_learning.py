"""Bounded supervised learning for a unit's internal output projection.

This module updates only w_yx, w_ym, w_yc and b_y. It does not differentiate
through the recurrent state transition or update the unit's internal dynamics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ama.ana.unit import (
    NeuralUnitParameters,
    NeuralUnitState,
    Vector,
    _as_vector,
)


@dataclass(frozen=True, slots=True)
class UnitLearningPolicy:
    """Learning rate and hard bounds for local output-projection updates."""

    learning_rate: float = 0.01
    max_abs_weight: float = 5.0
    max_abs_update: float = 0.05
    max_abs_feature: float = 10.0
    max_abs_target: float = 1.0

    def __post_init__(self) -> None:
        for name in (
            "learning_rate",
            "max_abs_weight",
            "max_abs_update",
            "max_abs_feature",
            "max_abs_target",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True, slots=True)
class UnitLearningResult:
    """One local update; prediction and error are measured before the update."""

    parameters: NeuralUnitParameters
    prediction: Vector
    error: Vector
    max_abs_update_applied: float


def _bounded_delta(
    gradient: float,
    current: float,
    policy: UnitLearningPolicy,
) -> tuple[float, float]:
    delta = max(
        -policy.max_abs_update,
        min(policy.max_abs_update, policy.learning_rate * gradient),
    )
    updated = max(
        -policy.max_abs_weight,
        min(policy.max_abs_weight, current + delta),
    )
    return updated, updated - current


def _update_matrix(
    matrix: tuple[tuple[float, ...], ...],
    feature: Vector,
    delta_signal: Vector,
    policy: UnitLearningPolicy,
) -> tuple[tuple[tuple[float, ...], ...], tuple[tuple[float, ...], ...]]:
    updated_rows = []
    update_rows = []
    for row, signal in zip(matrix, delta_signal):
        updated_row = []
        update_row = []
        for weight, value in zip(row, feature):
            updated, delta = _bounded_delta(signal * value, weight, policy)
            updated_row.append(updated)
            update_row.append(delta)
        updated_rows.append(tuple(updated_row))
        update_rows.append(tuple(update_row))
    return tuple(updated_rows), tuple(update_rows)


def supervised_unit_output_step(
    parameters: NeuralUnitParameters,
    state: NeuralUnitState,
    target: Vector,
    policy: UnitLearningPolicy = UnitLearningPolicy(),
) -> UnitLearningResult:
    """Fit the unit's internal tanh output projection to a supervised target.

    The local prediction is recomputed from the supplied state. For squared
    error, the output delta is (target - prediction) * (1 - prediction**2).
    Only output-projection matrices and bias are updated. State-transition
    matrices (x, memory, context and modulation dynamics) remain unchanged.
    """
    if not isinstance(parameters, NeuralUnitParameters):
        raise ValueError("parameters must be NeuralUnitParameters")
    if not isinstance(state, NeuralUnitState):
        raise ValueError("state must be NeuralUnitState")
    if not isinstance(policy, UnitLearningPolicy):
        raise ValueError("policy must be UnitLearningPolicy")

    internal_size = parameters.internal_size
    x = _as_vector(state.x, "state.x", internal_size)
    memory = _as_vector(state.m, "state.m", internal_size)
    context = _as_vector(state.c, "state.c", internal_size)
    _as_vector(state.g, "state.g", internal_size)
    _as_vector(state.y, "state.y", parameters.output_size)
    checked_target = _as_vector(target, "target", parameters.output_size)

    features = x + memory + context
    if any(abs(value) > policy.max_abs_feature for value in features):
        raise ValueError("state feature exceeds max_abs_feature")
    if any(abs(value) > policy.max_abs_target for value in checked_target):
        raise ValueError("target exceeds max_abs_target")

    logits = tuple(
        sum(a * b for a, b in zip(parameters.w_yx[index], x))
        + sum(a * b for a, b in zip(parameters.w_ym[index], memory))
        + sum(a * b for a, b in zip(parameters.w_yc[index], context))
        + parameters.b_y[index]
        for index in range(parameters.output_size)
    )
    prediction = tuple(math.tanh(value) for value in logits)
    error = tuple(desired - actual for desired, actual in zip(checked_target, prediction))
    delta_signal = tuple(
        difference * (1.0 - actual * actual)
        for difference, actual in zip(error, prediction)
    )

    w_yx, updates_x = _update_matrix(
        parameters.w_yx, x, delta_signal, policy
    )
    w_ym, updates_m = _update_matrix(
        parameters.w_ym, memory, delta_signal, policy
    )
    w_yc, updates_c = _update_matrix(
        parameters.w_yc, context, delta_signal, policy
    )
    bias_values = []
    bias_updates = []
    for bias, signal in zip(parameters.b_y, delta_signal):
        updated, delta = _bounded_delta(signal, bias, policy)
        bias_values.append(updated)
        bias_updates.append(delta)

    updated_parameters = replace(
        parameters,
        w_yx=w_yx,
        w_ym=w_ym,
        w_yc=w_yc,
        b_y=tuple(bias_values),
    )
    all_updates = (
        *(value for row in updates_x for value in row),
        *(value for row in updates_m for value in row),
        *(value for row in updates_c for value in row),
        *bias_updates,
    )
    maximum = max((abs(value) for value in all_updates), default=0.0)
    return UnitLearningResult(
        parameters=updated_parameters,
        prediction=prediction,
        error=error,
        max_abs_update_applied=maximum,
    )
