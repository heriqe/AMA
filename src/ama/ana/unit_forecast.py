"""Held-out forecasting benchmark for locally trained ANA unit outputs."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

from ama.ana.unit import (
    NeuralUnitInput,
    NeuralUnitParameters,
    NeuralUnitState,
    step,
)
from ama.ana.unit_learning import (
    UnitLearningPolicy,
    supervised_unit_output_step,
)


@dataclass(frozen=True, slots=True)
class UnitForecastReport:
    """One paired sequence evaluation for fixed and trainable unit outputs."""

    seed: int
    train_steps: int
    evaluation_steps: int
    fixed_mse: float
    fixed_mae: float
    learned_mse: float
    learned_mae: float
    persistence_mse: float
    final_output_weight: float
    final_output_bias: float


@dataclass(frozen=True, slots=True)
class UnitForecastAggregate:
    """Population descriptive statistics for one unit forecast metric."""

    name: str
    mean_mse: float
    std_mse: float
    mean_mae: float
    std_mae: float


@dataclass(frozen=True, slots=True)
class UnitForecastSuiteReport:
    """Multi-seed paired unit forecasting results."""

    seeds: tuple[int, ...]
    reports: tuple[UnitForecastReport, ...]
    mean_persistence_mse: float
    std_persistence_mse: float
    aggregates: tuple[UnitForecastAggregate, ...]


def _unit_parameters() -> NeuralUnitParameters:
    """Fixed state dynamics; only the output projection is eligible to learn."""
    base = NeuralUnitParameters.zeros(
        input_size=1,
        relation_size=1,
        internal_size=1,
        output_size=1,
        rho=0.8,
        eta=0.1,
        gamma=0.2,
    )
    return replace(
        base,
        w_xx=((0.25,),),
        w_xu=((1.0,),),
        w_yx=((0.0,),),
    )


def _series(seed: int, count: int) -> tuple[float, ...]:
    rng = random.Random(seed)
    values = [rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4)]
    for _ in range(2, count):
        value = 0.78 * values[-1] + rng.gauss(0.0, 0.06)
        values.append(max(-0.95, min(0.95, value)))
    return tuple(values)


def _mse(errors: list[float]) -> float:
    return sum(value * value for value in errors) / len(errors)


def _mae(errors: list[float]) -> float:
    return sum(abs(value) for value in errors) / len(errors)


def _mean(values: tuple[float, ...]) -> float:
    return sum(values) / len(values)


def _population_std(values: tuple[float, ...]) -> float:
    average = _mean(values)
    return math.sqrt(sum((value - average) ** 2 for value in values) / len(values))


def run_unit_forecast_benchmark(
    seed: int = 41,
    train_steps: int = 300,
    evaluation_steps: int = 120,
) -> UnitForecastReport:
    """Train only a unit's output projection, then evaluate on future samples.

    The input sequence is a bounded synthetic AR(1) process. The state
    transition parameters are identical and frozen in both variants. During
    training, only w_yx and b_y of the trainable unit are updated. Evaluation
    is strictly frozen and follows the training segment in the same sequence.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    for name, value in (
        ("train_steps", train_steps),
        ("evaluation_steps", evaluation_steps),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
        if value < 20 or value > 10_000:
            raise ValueError(f"{name} must be between 20 and 10000")

    values = _series(seed, train_steps + evaluation_steps + 1)
    fixed_parameters = _unit_parameters()
    learned_parameters = _unit_parameters()
    fixed_state = NeuralUnitState.initial(fixed_parameters)
    learned_state = NeuralUnitState.initial(learned_parameters)
    policy = UnitLearningPolicy(
        learning_rate=0.05,
        max_abs_weight=2.0,
        max_abs_update=0.02,
        max_abs_feature=2.0,
        max_abs_target=1.0,
    )
    fixed_errors: list[float] = []
    learned_errors: list[float] = []
    persistence_errors: list[float] = []

    for index in range(train_steps + evaluation_steps):
        current = values[index]
        target = (values[index + 1],)
        signals = NeuralUnitInput(external=(current,), relational=(0.0,))

        fixed_state = step(fixed_state, signals, fixed_parameters)
        learned_state = step(learned_state, signals, learned_parameters)

        if index < train_steps:
            learned_parameters = supervised_unit_output_step(
                learned_parameters, learned_state, target, policy
            ).parameters
        else:
            fixed_errors.append(fixed_state.y[0] - target[0])
            learned_errors.append(learned_state.y[0] - target[0])
            persistence_errors.append(current - target[0])

    metrics = (
        _mse(fixed_errors),
        _mae(fixed_errors),
        _mse(learned_errors),
        _mae(learned_errors),
        _mse(persistence_errors),
        learned_parameters.w_yx[0][0],
        learned_parameters.b_y[0],
    )
    if not all(math.isfinite(value) for value in metrics):
        raise RuntimeError("unit forecast metrics must be finite")
    return UnitForecastReport(
        seed=seed,
        train_steps=train_steps,
        evaluation_steps=evaluation_steps,
        fixed_mse=metrics[0],
        fixed_mae=metrics[1],
        learned_mse=metrics[2],
        learned_mae=metrics[3],
        persistence_mse=metrics[4],
        final_output_weight=metrics[5],
        final_output_bias=metrics[6],
    )


def run_unit_forecast_suite(
    seeds: tuple[int, ...] = (2, 5, 11, 17, 29, 41, 53, 67, 79, 97),
    train_steps: int = 300,
    evaluation_steps: int = 120,
) -> UnitForecastSuiteReport:
    """Aggregate the paired unit forecasting experiment across unique seeds."""
    if not isinstance(seeds, tuple) or not seeds:
        raise ValueError("seeds must be a non-empty tuple")
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        raise ValueError("seeds must contain only integers")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique")

    reports = tuple(
        run_unit_forecast_benchmark(
            seed=seed,
            train_steps=train_steps,
            evaluation_steps=evaluation_steps,
        )
        for seed in seeds
    )
    metrics = (
        ("fixed", "fixed_mse", "fixed_mae"),
        ("learned", "learned_mse", "learned_mae"),
    )
    aggregates = []
    for name, mse_field, mae_field in metrics:
        mse_values = tuple(getattr(report, mse_field) for report in reports)
        mae_values = tuple(getattr(report, mae_field) for report in reports)
        aggregates.append(
            UnitForecastAggregate(
                name=name,
                mean_mse=_mean(mse_values),
                std_mse=_population_std(mse_values),
                mean_mae=_mean(mae_values),
                std_mae=_population_std(mae_values),
            )
        )
    persistence = tuple(report.persistence_mse for report in reports)
    return UnitForecastSuiteReport(
        seeds=seeds,
        reports=reports,
        mean_persistence_mse=_mean(persistence),
        std_persistence_mse=_population_std(persistence),
        aggregates=tuple(aggregates),
    )
