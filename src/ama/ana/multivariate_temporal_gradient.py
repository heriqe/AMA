"""Analytic multi-parameter temporal gradients for the scalar ANA unit.

This experiment differentiates the scalar recurrence with respect to both its
recurrent coefficient w_xx[0][0] and input coefficient w_xu[0][0]. It remains
a restricted reference case, not a general multi-unit learning algorithm.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

from ama.ana.unit import (
    NeuralUnitInput,
    NeuralUnitParameters,
    NeuralUnitState,
    step,
)
from ama.ana.temporal_gradient_validation import _validate_scalar_reference


@dataclass(frozen=True, slots=True)
class ParameterGradientComparison:
    recurrent_weight: float
    input_weight: float
    parameter_name: str
    parameter_value: float
    epsilon: float
    analytic_gradient: float
    finite_difference_gradient: float
    absolute_error: float
    relative_error: float


@dataclass(frozen=True, slots=True)
class MultivariateGradientReport:
    comparisons: tuple[ParameterGradientComparison, ...]
    analytic_sequence_evaluations: int
    finite_difference_sequence_evaluations: int
    scenario_count: int
    parameter_count: int
    sequence_steps: int


def _analytic_gradients(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    recurrent_weight: float,
    input_weight: float,
) -> tuple[float, float]:
    """Return exact MSE derivatives for recurrent and input coefficients."""
    output_weight = parameters.w_yx[0][0]
    previous_x = 0.0
    previous_recurrent_sensitivity = 0.0
    previous_input_sensitivity = 0.0
    recurrent_terms: list[float] = []
    input_terms: list[float] = []

    for current, target in zip(inputs, targets):
        current_x = math.tanh(
            recurrent_weight * previous_x + input_weight * current
        )
        derivative_factor = 1.0 - current_x * current_x
        recurrent_sensitivity = derivative_factor * (
            previous_x + recurrent_weight * previous_recurrent_sensitivity
        )
        input_sensitivity = derivative_factor * (
            current + recurrent_weight * previous_input_sensitivity
        )

        current_y = math.tanh(output_weight * current_x)
        output_factor = (1.0 - current_y * current_y) * output_weight
        error = current_y - target
        recurrent_terms.append(2.0 * error * output_factor * recurrent_sensitivity)
        input_terms.append(2.0 * error * output_factor * input_sensitivity)

        previous_x = current_x
        previous_recurrent_sensitivity = recurrent_sensitivity
        previous_input_sensitivity = input_sensitivity

    count = len(inputs)
    gradients = (sum(recurrent_terms) / count, sum(input_terms) / count)
    if not all(math.isfinite(value) for value in gradients):
        raise RuntimeError("analytic multi-parameter gradient is non-finite")
    return gradients


def _sequence_loss(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    recurrent_weight: float,
    input_weight: float,
) -> float:
    candidate = replace(
        parameters,
        w_xx=((recurrent_weight,),),
        w_xu=((input_weight,),),
    )
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
    loss = sum(squared_errors) / len(squared_errors)
    if not math.isfinite(loss):
        raise RuntimeError("sequence loss is non-finite")
    return loss


def compare_multivariate_temporal_gradients(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    *,
    scenarios: tuple[tuple[float, float], ...] = (
        (-0.4, 0.55),
        (0.0, 0.55),
        (0.3, 0.55),
        (0.7, 0.55),
    ),
    epsilons: tuple[float, ...] = (1e-3, 1e-4, 1e-5),
) -> MultivariateGradientReport:
    """Compare analytic and central-difference gradients for two parameters."""
    _validate_scalar_reference(parameters, inputs, targets)
    if not isinstance(scenarios, tuple) or not scenarios:
        raise ValueError("scenarios must be a non-empty tuple")
    if not isinstance(epsilons, tuple) or not epsilons:
        raise ValueError("epsilons must be a non-empty tuple")
    for scenario in scenarios:
        if not isinstance(scenario, tuple) or len(scenario) != 2:
            raise ValueError("each scenario must be a (recurrent_weight, input_weight) tuple")
        for value in scenario:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("scenario weights must be numeric")
            if not math.isfinite(value):
                raise ValueError("scenario weights must be finite")
    for epsilon in epsilons:
        if isinstance(epsilon, bool) or not isinstance(epsilon, (int, float)):
            raise ValueError("epsilons must be numeric")
        if not math.isfinite(epsilon) or epsilon <= 0.0:
            raise ValueError("epsilons must be finite and positive")

    comparisons = []
    for recurrent_weight, input_weight in scenarios:
        analytic_recurrent, analytic_input = _analytic_gradients(
            parameters, inputs, targets, recurrent_weight, input_weight
        )
        for parameter_name, value, analytic in (
            ("w_xx[0][0]", recurrent_weight, analytic_recurrent),
            ("w_xu[0][0]", input_weight, analytic_input),
        ):
            for epsilon in epsilons:
                if parameter_name == "w_xx[0][0]":
                    plus = _sequence_loss(
                        parameters, inputs, targets,
                        recurrent_weight + epsilon, input_weight,
                    )
                    minus = _sequence_loss(
                        parameters, inputs, targets,
                        recurrent_weight - epsilon, input_weight,
                    )
                else:
                    plus = _sequence_loss(
                        parameters, inputs, targets,
                        recurrent_weight, input_weight + epsilon,
                    )
                    minus = _sequence_loss(
                        parameters, inputs, targets,
                        recurrent_weight, input_weight - epsilon,
                    )
                numerical = (plus - minus) / (2.0 * epsilon)
                absolute = abs(analytic - numerical)
                relative = absolute / max(abs(analytic), 1e-12)
                comparisons.append(ParameterGradientComparison(
                    recurrent_weight=float(recurrent_weight),
                    input_weight=float(input_weight),
                    parameter_name=parameter_name,
                    parameter_value=float(value),
                    epsilon=float(epsilon),
                    analytic_gradient=analytic,
                    finite_difference_gradient=numerical,
                    absolute_error=absolute,
                    relative_error=relative,
                ))

    return MultivariateGradientReport(
        comparisons=tuple(comparisons),
        analytic_sequence_evaluations=len(scenarios),
        finite_difference_sequence_evaluations=2 * len(comparisons),
        scenario_count=len(scenarios),
        parameter_count=2,
        sequence_steps=len(inputs),
    )
