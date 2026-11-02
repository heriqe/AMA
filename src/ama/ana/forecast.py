"""One-step forecasting benchmark using the complete recurrent ANA network.

The network parameters remain fixed. A bounded scalar readout is trained online
on the training segment; candidate edge plasticity is compared independently.
Evaluation targets are never used to update the readout or edge plasticity.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

from ama.ana.learning import LearningParameters, LearningState, supervised_step
from ama.ana.network import (
    Connection,
    NetworkDefinition,
    NetworkNode,
    NetworkState,
    step_network,
)
from ama.ana.plasticity import (
    PlasticityParameters,
    PlasticityState,
    step_plasticity,
)
from ama.ana.unit import NeuralUnitParameters, Vector


@dataclass(frozen=True, slots=True)
class ForecastVariant:
    """Held-out forecasting metrics for one network adaptation strategy."""

    name: str
    mean_squared_error: float
    mean_absolute_error: float
    final_edge_weight: float
    final_edge_active: bool


@dataclass(frozen=True, slots=True)
class ForecastBenchmarkReport:
    """Reproducible temporal train/evaluation split and its forecast results."""

    seed: int
    train_steps: int
    evaluation_steps: int
    persistence_baseline_mse: float
    variants: tuple[ForecastVariant, ...]


def _unit_parameters(*, sensor: bool) -> NeuralUnitParameters:
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=1
    )
    if sensor:
        return replace(
            base,
            w_xu=((0.8,),),
            w_xx=((0.15,),),
            w_xm=((0.1,),),
            w_yx=((0.9,),),
            w_ym=((0.2,),),
        )
    return replace(
        base,
        w_xr=((0.7,),),
        w_xx=((0.2,),),
        w_xm=((0.15,),),
        w_yx=((0.9,),),
        w_ym=((0.25,),),
    )


def _series(seed: int, count: int) -> tuple[float, ...]:
    """Generate a bounded, stationary AR(2)-like sequence."""
    rng = random.Random(seed)
    values = [rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)]
    for _ in range(count - 2):
        value = 0.72 * values[-1] - 0.18 * values[-2] + rng.gauss(0.0, 0.08)
        values.append(max(-1.0, min(1.0, value)))
    return tuple(values)


def _features(state) -> Vector:
    by_id = {item.node_id: item.state for item in state.nodes}
    sensor = by_id["sensor"]
    integrator = by_id["integrator"]
    return (
        sensor.x[0],
        sensor.m[0],
        sensor.y[0],
        integrator.x[0],
        integrator.m[0],
        integrator.y[0],
        1.0,
    )


def _network(weight: float, active: bool) -> NetworkDefinition:
    edges = (Connection("sensor", "integrator", weight),) if active else ()
    return NetworkDefinition(
        nodes=(
            NetworkNode("sensor", _unit_parameters(sensor=True)),
            NetworkNode("integrator", _unit_parameters(sensor=False)),
        ),
        connections=edges,
    )


def run_forecast_benchmark(
    seed: int = 23,
    train_steps: int = 300,
    evaluation_steps: int = 120,
) -> ForecastBenchmarkReport:
    """Compare fixed, weight-adaptive and structural networks on held-out data.

    The same generated sequence and readout rule are used for all variants.
    The readout is trained only during the first `train_steps`. Edge adaptation
    also stops at the train/evaluation boundary. The network's recurrent state
    continues naturally across that boundary.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    for name, value in (("train_steps", train_steps), ("evaluation_steps", evaluation_steps)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
        if value < 20 or value > 10_000:
            raise ValueError(f"{name} must be between 20 and 10000")

    values = _series(seed, train_steps + evaluation_steps + 1)
    readout_parameters = LearningParameters(
        learning_rate=0.04,
        eligibility_decay=0.8,
        baseline_rate=0.05,
        max_abs_weight=5.0,
        max_abs_update=0.05,
        max_abs_signal=10.0,
    )
    edge_parameters = PlasticityParameters(
        learning_rate=0.04,
        weight_decay=0.01,
        max_abs_weight=0.8,
        activation_threshold=0.15,
        activation_steps=3,
        prune_threshold=0.015,
        prune_steps=8,
        max_abs_activity=1.0,
        initial_weight=0.05,
    )

    states = {
        name: NetworkState.initial(_network(0.05, True))
        for name in ("fixed", "weight_only", "structural")
    }
    readouts = {
        name: LearningState.initial((0.0,) * 7)
        for name in ("fixed", "weight_only", "structural")
    }
    weight_only_weight = 0.05
    structural = PlasticityState.initial((("sensor", "integrator"),))
    errors = {
        name: {"squared": 0.0, "absolute": 0.0, "count": 0}
        for name in ("fixed", "weight_only", "structural")
    }
    persistence_squared = 0.0

    for index in range(train_steps + evaluation_steps):
        current = values[index]
        target = values[index + 1]
        training = index < train_steps

        for name in ("fixed", "weight_only", "structural"):
            if name == "fixed":
                weight, active = 0.05, True
            elif name == "weight_only":
                weight, active = weight_only_weight, True
            else:
                edge = structural.connections[0]
                weight, active = edge.weight, edge.active

            graph = _network(weight, active)
            next_state = step_network(
                graph,
                states[name],
                {"sensor": (current,), "integrator": (0.0,)},
            )
            features = _features(next_state)
            prediction = sum(
                coefficient * feature
                for coefficient, feature in zip(readouts[name].weights, features)
            )

            if training:
                result = supervised_step(
                    readouts[name], features, target, readout_parameters
                )
                readouts[name] = result.state
            else:
                bounded_prediction = max(-1.0, min(1.0, prediction))
                error = bounded_prediction - target
                errors[name]["squared"] += error * error
                errors[name]["absolute"] += abs(error)
                errors[name]["count"] += 1

            states[name] = next_state

            # Both adaptive variants use the same bounded Hebbian weight rule.
            # Only the structural variant may activate or prune the candidate.
            if training and name in ("weight_only", "structural"):
                activities = {
                    "sensor": next_state.nodes[0].state.y[0],
                    "integrator": next_state.nodes[1].state.y[0],
                }
                pre, post = activities["sensor"], activities["integrator"]
                if name == "weight_only":
                    raw = (
                        weight_only_weight
                        + edge_parameters.learning_rate * pre * post
                        - edge_parameters.weight_decay * weight_only_weight
                    )
                    weight_only_weight = max(
                        -edge_parameters.max_abs_weight,
                        min(edge_parameters.max_abs_weight, raw),
                    )
                else:
                    structural = step_plasticity(
                        structural, activities, edge_parameters
                    )

        if not training:
            persistence_error = current - target
            persistence_squared += persistence_error * persistence_error

    variants = []
    for name in ("fixed", "weight_only", "structural"):
        count = errors[name]["count"]
        if count != evaluation_steps:
            raise RuntimeError("forecast evaluation count does not match protocol")
        if name == "fixed":
            final_weight, final_active = 0.05, True
        elif name == "weight_only":
            final_weight, final_active = weight_only_weight, True
        else:
            final = structural.connections[0]
            final_weight, final_active = final.weight, final.active
        mse = errors[name]["squared"] / count
        mae = errors[name]["absolute"] / count
        if not math.isfinite(mse) or not math.isfinite(mae):
            raise RuntimeError("forecast metrics must be finite")
        variants.append(
            ForecastVariant(
                name=name,
                mean_squared_error=mse,
                mean_absolute_error=mae,
                final_edge_weight=final_weight,
                final_edge_active=final_active,
            )
        )

    return ForecastBenchmarkReport(
        seed=seed,
        train_steps=train_steps,
        evaluation_steps=evaluation_steps,
        persistence_baseline_mse=persistence_squared / evaluation_steps,
        variants=tuple(variants),
    )


@dataclass(frozen=True, slots=True)
class ForecastAggregate:
    """Population summary for one strategy across independent seeds."""

    name: str
    mean_mse: float
    std_mse: float
    mean_mae: float
    std_mae: float


@dataclass(frozen=True, slots=True)
class ForecastSuiteReport:
    """Multi-seed forecast results with paired per-seed reports retained."""

    seeds: tuple[int, ...]
    reports: tuple[ForecastBenchmarkReport, ...]
    mean_persistence_mse: float
    std_persistence_mse: float
    aggregates: tuple[ForecastAggregate, ...]


def _mean(values: tuple[float, ...]) -> float:
    return sum(values) / len(values)


def _population_std(values: tuple[float, ...]) -> float:
    average = _mean(values)
    return math.sqrt(sum((value - average) ** 2 for value in values) / len(values))


def run_forecast_suite(
    seeds: tuple[int, ...] = (3, 7, 11, 19, 23, 31, 43, 59, 71, 89),
    train_steps: int = 300,
    evaluation_steps: int = 120,
) -> ForecastSuiteReport:
    """Aggregate identical forecasting protocols over independent RNG seeds.

    Per-seed reports are retained so strategy comparisons remain paired on
    identical generated data. Standard deviations are population descriptive
    statistics, not confidence intervals or significance tests.
    """
    if not isinstance(seeds, tuple) or not seeds:
        raise ValueError("seeds must be a non-empty tuple")
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        raise ValueError("every seed must be an integer")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique")

    reports = tuple(
        run_forecast_benchmark(
            seed=seed,
            train_steps=train_steps,
            evaluation_steps=evaluation_steps,
        )
        for seed in seeds
    )
    names = tuple(item.name for item in reports[0].variants)
    aggregates = []
    for name in names:
        variants = tuple(
            next(item for item in report.variants if item.name == name)
            for report in reports
        )
        mse_values = tuple(item.mean_squared_error for item in variants)
        mae_values = tuple(item.mean_absolute_error for item in variants)
        aggregates.append(
            ForecastAggregate(
                name=name,
                mean_mse=_mean(mse_values),
                std_mse=_population_std(mse_values),
                mean_mae=_mean(mae_values),
                std_mae=_population_std(mae_values),
            )
        )

    baseline_values = tuple(report.persistence_baseline_mse for report in reports)
    return ForecastSuiteReport(
        seeds=seeds,
        reports=reports,
        mean_persistence_mse=_mean(baseline_values),
        std_persistence_mse=_population_std(baseline_values),
        aggregates=tuple(aggregates),
    )
