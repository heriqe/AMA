"""Finite-difference temporal credit assignment for one recurrent ANA unit.

This experimental optimizer changes only w_xx[0][0]. It evaluates the loss
over an entire sequence, so each parameter perturbation is credited against
the downstream temporal consequences of that recurrent coefficient.
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


@dataclass(frozen=True, slots=True)
class TemporalCreditPolicy:
    """Hard-bounded coordinate update policy for temporal finite differences."""

    learning_rate: float = 0.5
    finite_difference_epsilon: float = 1e-4
    max_abs_weight: float = 1.5
    max_abs_update: float = 0.02
    max_abs_signal: float = 1.0
    epochs: int = 100

    def __post_init__(self) -> None:
        for name in (
            "learning_rate",
            "finite_difference_epsilon",
            "max_abs_weight",
            "max_abs_update",
            "max_abs_signal",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        if (
            isinstance(self.epochs, bool)
            or not isinstance(self.epochs, int)
            or not 1 <= self.epochs <= 2_000
        ):
            raise ValueError("epochs must be an integer between 1 and 2000")


@dataclass(frozen=True, slots=True)
class TemporalCreditResult:
    """Result of sequence-level optimization of one recurrent coefficient."""

    parameters: NeuralUnitParameters
    initial_mse: float
    final_mse: float
    epochs_completed: int
    updates_applied: int
    final_recurrent_weight: float


@dataclass(frozen=True, slots=True)
class TemporalCreditBenchmarkReport:
    """Paired held-out evaluation of fixed and learned recurrent dynamics."""

    seed: int
    train_steps: int
    evaluation_steps: int
    fixed_mse: float
    learned_mse: float
    fixed_mae: float
    learned_mae: float
    initial_train_mse: float
    final_train_mse: float
    initial_recurrent_weight: float
    learned_recurrent_weight: float


def _replace_recurrent_weight(
    parameters: NeuralUnitParameters,
    value: float,
) -> NeuralUnitParameters:
    matrix = (tuple((value,)),)
    return replace(parameters, w_xx=matrix)


def _sequence_mse(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
) -> float:
    state = NeuralUnitState.initial(parameters)
    squared_errors = []
    for current, target in zip(inputs, targets):
        state = step(
            state,
            NeuralUnitInput(external=(current,), relational=(0.0,)),
            parameters,
        )
        difference = state.y[0] - target
        squared_errors.append(difference * difference)
    result = sum(squared_errors) / len(squared_errors)
    if not math.isfinite(result):
        raise RuntimeError("temporal loss must be finite")
    return result


def _validate_sequence(
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    policy: TemporalCreditPolicy,
) -> None:
    if not isinstance(inputs, tuple) or not isinstance(targets, tuple):
        raise ValueError("inputs and targets must be tuples")
    if len(inputs) != len(targets) or len(inputs) < 2:
        raise ValueError("inputs and targets must have equal length of at least 2")
    for name, values in (("inputs", inputs), ("targets", targets)):
        for value in values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must contain only numeric values")
            if not math.isfinite(value):
                raise ValueError(f"{name} must contain only finite values")
            if abs(value) > policy.max_abs_signal:
                raise ValueError(f"{name} exceeds max_abs_signal")


def fit_recurrent_weight(
    parameters: NeuralUnitParameters,
    inputs: tuple[float, ...],
    targets: tuple[float, ...],
    policy: TemporalCreditPolicy = TemporalCreditPolicy(),
) -> TemporalCreditResult:
    """Fit only w_xx[0][0] using central finite differences over a full sequence.

    The loss is the mean squared output error after replaying the entire input
    sequence from the initial state. Central differences approximate the
    derivative of that sequence-level loss with respect to the recurrent
    coefficient. This is a black-box temporal credit method, not BPTT.
    """
    if not isinstance(parameters, NeuralUnitParameters):
        raise ValueError("parameters must be NeuralUnitParameters")
    if (
        parameters.input_size != 1
        or parameters.relation_size != 1
        or parameters.internal_size != 1
        or parameters.output_size != 1
    ):
        raise ValueError("temporal credit currently requires a 1x1 unit")
    if not isinstance(policy, TemporalCreditPolicy):
        raise ValueError("policy must be TemporalCreditPolicy")
    _validate_sequence(inputs, targets, policy)

    current = parameters.w_xx[0][0]
    if abs(current) > policy.max_abs_weight:
        raise ValueError("initial recurrent weight exceeds max_abs_weight")
    initial_loss = _sequence_mse(parameters, inputs, targets)
    current_parameters = parameters
    updates = 0

    for _ in range(policy.epochs):
        current = current_parameters.w_xx[0][0]
        plus = min(policy.max_abs_weight, current + policy.finite_difference_epsilon)
        minus = max(-policy.max_abs_weight, current - policy.finite_difference_epsilon)
        if plus == minus:
            break
        plus_loss = _sequence_mse(
            _replace_recurrent_weight(current_parameters, plus), inputs, targets
        )
        minus_loss = _sequence_mse(
            _replace_recurrent_weight(current_parameters, minus), inputs, targets
        )
        gradient = (plus_loss - minus_loss) / (plus - minus)
        if not math.isfinite(gradient):
            raise RuntimeError("temporal gradient estimate must be finite")
        delta = max(
            -policy.max_abs_update,
            min(policy.max_abs_update, -policy.learning_rate * gradient),
        )
        updated = max(
            -policy.max_abs_weight,
            min(policy.max_abs_weight, current + delta),
        )
        if updated != current:
            current_parameters = _replace_recurrent_weight(
                current_parameters, updated
            )
            updates += 1

    final_loss = _sequence_mse(current_parameters, inputs, targets)
    return TemporalCreditResult(
        parameters=current_parameters,
        initial_mse=initial_loss,
        final_mse=final_loss,
        epochs_completed=policy.epochs,
        updates_applied=updates,
        final_recurrent_weight=current_parameters.w_xx[0][0],
    )


def _unit_parameters() -> NeuralUnitParameters:
    base = NeuralUnitParameters.zeros(
        input_size=1,
        relation_size=1,
        internal_size=1,
        output_size=1,
        rho=0.8,
        eta=0.0,
        gamma=0.0,
    )
    return replace(
        base,
        w_xu=((0.55,),),
        w_yx=((1.0,),),
        w_xx=((0.0,),),
    )


def run_temporal_credit_benchmark(
    seed: int = 41,
    train_steps: int = 300,
    evaluation_steps: int = 120,
) -> TemporalCreditBenchmarkReport:
    """Compare fixed dynamics with sequence-trained recurrence on held-out data."""
    import random

    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    for name, value in (
        ("train_steps", train_steps),
        ("evaluation_steps", evaluation_steps),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
        if value < 20 or value > 5_000:
            raise ValueError(f"{name} must be between 20 and 5000")

    rng = random.Random(seed)
    inputs = tuple(
        rng.uniform(-0.3, 0.3)
        for _ in range(train_steps + evaluation_steps)
    )
    targets = tuple(
        0.55 * current + 0.35 * (inputs[index - 1] if index else 0.0)
        for index, current in enumerate(inputs)
    )
    train_inputs = inputs[:train_steps]
    train_targets = targets[:train_steps]
    eval_inputs = inputs[train_steps:]
    eval_targets = targets[train_steps:]

    fixed_parameters = _unit_parameters()
    policy = TemporalCreditPolicy(
        learning_rate=0.5,
        finite_difference_epsilon=1e-4,
        max_abs_weight=1.0,
        max_abs_update=0.02,
        max_abs_signal=1.0,
        epochs=100,
    )
    trained = fit_recurrent_weight(
        fixed_parameters, train_inputs, train_targets, policy
    )
    learned_parameters = trained.parameters

    fixed_state = NeuralUnitState.initial(fixed_parameters)
    learned_state = NeuralUnitState.initial(learned_parameters)
    for current in train_inputs:
        signals = NeuralUnitInput(external=(current,), relational=(0.0,))
        fixed_state = step(fixed_state, signals, fixed_parameters)
        learned_state = step(learned_state, signals, learned_parameters)

    fixed_squared = []
    learned_squared = []
    fixed_absolute = []
    learned_absolute = []
    for current, target in zip(eval_inputs, eval_targets):
        signals = NeuralUnitInput(external=(current,), relational=(0.0,))
        fixed_state = step(fixed_state, signals, fixed_parameters)
        learned_state = step(learned_state, signals, learned_parameters)
        fixed_error = fixed_state.y[0] - target
        learned_error = learned_state.y[0] - target
        fixed_squared.append(fixed_error * fixed_error)
        learned_squared.append(learned_error * learned_error)
        fixed_absolute.append(abs(fixed_error))
        learned_absolute.append(abs(learned_error))

    metrics = (
        sum(fixed_squared) / len(fixed_squared),
        sum(learned_squared) / len(learned_squared),
        sum(fixed_absolute) / len(fixed_absolute),
        sum(learned_absolute) / len(learned_absolute),
        trained.initial_mse,
        trained.final_mse,
    )
    if not all(math.isfinite(value) for value in metrics):
        raise RuntimeError("temporal credit benchmark metrics must be finite")
    return TemporalCreditBenchmarkReport(
        seed=seed,
        train_steps=train_steps,
        evaluation_steps=evaluation_steps,
        fixed_mse=metrics[0],
        learned_mse=metrics[1],
        fixed_mae=metrics[2],
        learned_mae=metrics[3],
        initial_train_mse=metrics[4],
        final_train_mse=metrics[5],
        initial_recurrent_weight=fixed_parameters.w_xx[0][0],
        learned_recurrent_weight=learned_parameters.w_xx[0][0],
    )
