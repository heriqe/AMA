"""Analytic reference gradients for the scalar ANA temporal-credit experiment.

The derivation is intentionally restricted to the benchmark's scalar regime:
x_t = tanh(w * x_(t-1) + a * u_t), y_t = tanh(v * x_t).
All other state pathways must be zero so this analytic derivative is an
independent reference for the finite-difference optimizer, not a general ANA
gradient implementation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import NeuralUnitInput, NeuralUnitParameters, NeuralUnitState, step


@dataclass(frozen=True, slots=True)
class GradientComparison:
    recurrent_weight: float
    epsilon: float
    analytic_gradient: float
    finite_difference_gradient: float
    absolute_error: float
    relative_error: float


@dataclass(frozen=True, slots=True)
class TemporalGradientValidationReport:
    comparisons: tuple[GradientComparison, ...]
    analytic_sequence_evaluations: int
    finite_difference_sequence_evaluations: int
    sequence_steps: int


def _validate_scalar_reference(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
) -> None:
    if not isinstance(parameters, NeuralUnitParameters):
        raise ValueError("parameters must be NeuralUnitParameters")
    if (parameters.input_size, parameters.relation_size,
        parameters.internal_size, parameters.output_size) != (1, 1, 1, 1):
        raise ValueError("analytic reference requires a 1x1 ANA unit")
    if not isinstance(inputs, tuple) or not isinstance(targets, tuple):
        raise ValueError("inputs and targets must be tuples")
    if len(inputs) < 2 or len(inputs) != len(targets):
        raise ValueError("inputs and targets must have equal length of at least 2")
    for name, values in (("inputs", inputs), ("targets", targets)):
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must contain numeric values")
            if not math.isfinite(value):
                raise ValueError(f"{name} must contain finite values")

    zero_matrices = (
        parameters.w_xm, parameters.w_xc, parameters.w_xr,
        parameters.w_cc, parameters.w_cx, parameters.w_cr,
        parameters.w_gx, parameters.w_gc, parameters.w_gm,
        parameters.w_mx, parameters.w_mc, parameters.w_mu,
        parameters.w_ym, parameters.w_yc,
    )
    zero_vectors = (parameters.b_x, parameters.b_c, parameters.b_g,
                    parameters.b_m, parameters.b_y)
    if any(any(value != 0.0 for row in matrix for value in row)
           for matrix in zero_matrices):
        raise ValueError("non-reference state pathways must be zero")
    if any(any(value != 0.0 for value in vector) for vector in zero_vectors):
        raise ValueError("reference bias vectors must be zero")


def _loss_and_analytic_gradient(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    recurrent_weight: float,
) -> tuple[float, float]:
    """Return sequence MSE and its exact derivative w.r.t. w_xx[0][0]."""
    weight = recurrent_weight
    input_weight = parameters.w_xu[0][0]
    output_weight = parameters.w_yx[0][0]
    previous_x = 0.0
    previous_sensitivity = 0.0
    squared_errors: list[float] = []
    gradient_terms: list[float] = []

    for current, target in zip(inputs, targets):
        preactivation = weight * previous_x + input_weight * current
        current_x = math.tanh(preactivation)
        current_sensitivity = (1.0 - current_x * current_x) * (
            previous_x + weight * previous_sensitivity
        )
        current_y = math.tanh(output_weight * current_x)
        output_sensitivity = (
            (1.0 - current_y * current_y)
            * output_weight
            * current_sensitivity
        )
        error = current_y - target
        squared_errors.append(error * error)
        gradient_terms.append(2.0 * error * output_sensitivity)
        previous_x = current_x
        previous_sensitivity = current_sensitivity

    count = len(inputs)
    loss = sum(squared_errors) / count
    gradient = sum(gradient_terms) / count
    if not math.isfinite(loss) or not math.isfinite(gradient):
        raise RuntimeError("analytic reference produced a non-finite result")
    return loss, gradient


def _sequence_loss(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    recurrent_weight: float,
) -> float:
    from dataclasses import replace

    candidate = replace(parameters, w_xx=((recurrent_weight,),))
    state = NeuralUnitState.initial(candidate)
    squared_errors = []
    for current, target in zip(inputs, targets):
        state = step(
            state,
            NeuralUnitInput(external=(current,), relational=(0.0,)),
            candidate,
        )
        difference = state.y[0] - target
        squared_errors.append(difference * difference)
    return sum(squared_errors) / len(squared_errors)


def compare_temporal_gradients(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    *,
    recurrent_weights: tuple[float, ...] = (-0.4, 0.0, 0.3, 0.7),
    epsilons: tuple[float, ...] = (1e-2, 1e-3, 1e-4, 1e-5, 1e-6),
) -> TemporalGradientValidationReport:
    """Compare exact scalar temporal sensitivity with central differences."""
    _validate_scalar_reference(parameters, inputs, targets)
    if not isinstance(recurrent_weights, tuple) or not recurrent_weights:
        raise ValueError("recurrent_weights must be a non-empty tuple")
    if not isinstance(epsilons, tuple) or not epsilons:
        raise ValueError("epsilons must be a non-empty tuple")
    for name, values in (("recurrent_weights", recurrent_weights),
                         ("epsilons", epsilons)):
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must contain numeric values")
            if not math.isfinite(value):
                raise ValueError(f"{name} must contain finite values")
    if any(epsilon <= 0.0 for epsilon in epsilons):
        raise ValueError("epsilons must be positive")

    comparisons = []
    for weight in recurrent_weights:
        _, analytic = _loss_and_analytic_gradient(parameters, inputs, targets, weight)
        for epsilon in epsilons:
            plus = _sequence_loss(parameters, inputs, targets, weight + epsilon)
            minus = _sequence_loss(parameters, inputs, targets, weight - epsilon)
            numerical = (plus - minus) / (2.0 * epsilon)
            absolute = abs(analytic - numerical)
            relative = absolute / max(abs(analytic), 1e-12)
            comparisons.append(GradientComparison(
                recurrent_weight=float(weight),
                epsilon=float(epsilon),
                analytic_gradient=analytic,
                finite_difference_gradient=numerical,
                absolute_error=absolute,
                relative_error=relative,
            ))

    return TemporalGradientValidationReport(
        comparisons=tuple(comparisons),
        analytic_sequence_evaluations=len(recurrent_weights),
        finite_difference_sequence_evaluations=2 * len(comparisons),
        sequence_steps=len(inputs),
    )
