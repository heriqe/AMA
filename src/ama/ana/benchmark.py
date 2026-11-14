"""Deterministic mechanism-level benchmarks for ANA v0.5 plasticity."""

from __future__ import annotations

import math
import random
from collections.abc import Iterable
from dataclasses import dataclass

from ama.ana.plasticity import (
    PlasticityParameters,
    PlasticityState,
    step_plasticity,
)


@dataclass(frozen=True, slots=True)
class PlasticityBenchmarkVariant:
    name: str
    mean_absolute_tracking_error: float
    mean_absolute_weight: float
    active_step_fraction: float
    activations: int
    deactivations: int
    max_abs_weight_observed: float
    final_weight: float
    final_active: bool


@dataclass(frozen=True, slots=True)
class PlasticityBenchmarkReport:
    steps_per_phase: int
    targets: tuple[float, ...]
    variants: tuple[PlasticityBenchmarkVariant, ...]


@dataclass(frozen=True, slots=True)
class PlasticityRobustnessVariant:
    name: str
    mean_absolute_tracking_error: float
    between_seed_error_stddev: float
    mean_active_step_fraction: float
    mean_activations: float
    mean_deactivations: float
    max_abs_weight_observed: float


@dataclass(frozen=True, slots=True)
class PlasticityRobustnessReport:
    steps_per_phase: int
    noise_amplitude: float
    seeds: tuple[int, ...]
    variants: tuple[PlasticityRobustnessVariant, ...]


def _validate_steps_per_phase(steps_per_phase: int) -> None:
    if isinstance(steps_per_phase, bool) or not isinstance(steps_per_phase, int):
        raise ValueError("steps_per_phase must be an integer")
    if not 1 <= steps_per_phase <= 10_000:
        raise ValueError("steps_per_phase must be between 1 and 10000")


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a mean without observations")
    return math.fsum(values) / len(values)


def _population_stddev(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a standard deviation without observations")
    average = _mean(values)
    variance = math.fsum((value - average) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def run_plasticity_benchmark(steps_per_phase: int = 40) -> PlasticityBenchmarkReport:
    """Compare fixed, weight-only and structural variants on four deterministic phases.

    The target is the product of two bounded activities. Tracking error is a
    mechanism-level proxy, not prediction error or a measure of cognition.
    """
    _validate_steps_per_phase(steps_per_phase)

    targets = (1.0, -1.0, 0.0, 1.0)
    activity_pairs = ((1.0, 1.0), (1.0, -1.0), (0.0, 0.0), (1.0, 1.0))
    structural_parameters = PlasticityParameters(
        learning_rate=0.2,
        weight_decay=0.1,
        max_abs_weight=1.0,
        activation_threshold=0.5,
        activation_steps=3,
        prune_threshold=0.08,
        prune_steps=3,
        max_abs_activity=1.0,
        initial_weight=0.05,
    )
    weight_only_parameters = PlasticityParameters(
        learning_rate=0.2,
        weight_decay=0.1,
        max_abs_weight=1.0,
        activation_threshold=0.5,
        activation_steps=3,
        prune_threshold=0.0,
        prune_steps=3,
        max_abs_activity=1.0,
        initial_weight=0.05,
    )

    fixed_weight = 0.05
    weight_only = PlasticityState.initial((("pre", "post"),), (0.05,))
    structural = PlasticityState.initial((("pre", "post"),))
    accumulators = {
        name: {"errors": [], "magnitudes": [], "active": [], "max_abs": 0.0}
        for name in ("fixed", "weight_only", "structural")
    }
    activations = 0
    deactivations = 0

    for target, (pre, post) in zip(targets, activity_pairs):
        for _ in range(steps_per_phase):
            old_structural_active = structural.connections[0].active
            activities = {"pre": pre, "post": post}
            weight_only = step_plasticity(weight_only, activities, weight_only_parameters)
            structural = step_plasticity(structural, activities, structural_parameters)

            structural_edge = structural.connections[0]
            if not old_structural_active and structural_edge.active:
                activations += 1
            elif old_structural_active and not structural_edge.active:
                deactivations += 1

            values = {
                "fixed": (fixed_weight, True),
                "weight_only": (weight_only.connections[0].weight, weight_only.connections[0].active),
                "structural": (structural_edge.weight, structural_edge.active),
            }
            for name, (weight, active) in values.items():
                metrics = accumulators[name]
                metrics["errors"].append(abs(weight - target))
                metrics["magnitudes"].append(abs(weight))
                metrics["active"].append(active)
                metrics["max_abs"] = max(metrics["max_abs"], abs(weight))

    variants = []
    for name in ("fixed", "weight_only", "structural"):
        metrics = accumulators[name]
        count = len(metrics["errors"])
        if count == 0:
            raise RuntimeError("benchmark produced no observations")
        mean_error = math.fsum(metrics["errors"]) / count
        mean_magnitude = math.fsum(metrics["magnitudes"]) / count
        active_fraction = sum(metrics["active"]) / count
        if not all(math.isfinite(value) for value in (mean_error, mean_magnitude, active_fraction)):
            raise RuntimeError("benchmark produced non-finite metrics")

        if name == "fixed":
            final_weight = fixed_weight
            final_active = True
            transition_activations = 0
            transition_deactivations = 0
        elif name == "weight_only":
            final_weight = weight_only.connections[0].weight
            final_active = weight_only.connections[0].active
            transition_activations = 0
            transition_deactivations = 0
        else:
            final_weight = structural.connections[0].weight
            final_active = structural.connections[0].active
            transition_activations = activations
            transition_deactivations = deactivations

        variants.append(
            PlasticityBenchmarkVariant(
                name=name,
                mean_absolute_tracking_error=mean_error,
                mean_absolute_weight=mean_magnitude,
                active_step_fraction=active_fraction,
                activations=transition_activations,
                deactivations=transition_deactivations,
                max_abs_weight_observed=metrics["max_abs"],
                final_weight=final_weight,
                final_active=final_active,
            )
        )

    return PlasticityBenchmarkReport(
        steps_per_phase=steps_per_phase,
        targets=targets,
        variants=tuple(variants),
    )


def run_noisy_plasticity_benchmark(
    steps_per_phase: int = 40,
    noise_amplitude: float = 0.1,
    seeds: Iterable[int] = (0, 1, 2, 3, 4),
) -> PlasticityRobustnessReport:
    """Compare variants on shared noisy streams across fixed random seeds.

    Uniform noise is independently added to each base activity and clipped
    to [-1, 1]. Each seed produces the same stream for all variants. The
    standard deviation is calculated across per-seed mean tracking errors.
    """
    _validate_steps_per_phase(steps_per_phase)
    if isinstance(noise_amplitude, bool) or not isinstance(noise_amplitude, (int, float)):
        raise ValueError("noise_amplitude must be numeric")
    try:
        noise = float(noise_amplitude)
    except OverflowError as error:
        raise ValueError("noise_amplitude must be finite") from error
    if not math.isfinite(noise) or not 0.0 <= noise <= 1.0:
        raise ValueError("noise_amplitude must be finite and in [0, 1]")

    try:
        seed_values = tuple(seeds)
    except TypeError as error:
        raise ValueError("seeds must be an iterable of non-negative integers") from error
    if not 1 <= len(seed_values) <= 100:
        raise ValueError("seeds must contain between 1 and 100 values")
    if any(isinstance(seed, bool) or not isinstance(seed, int) or seed < 0 for seed in seed_values):
        raise ValueError("seeds must contain only non-negative integers")
    if len(seed_values) != len(set(seed_values)):
        raise ValueError("seeds must be unique")
    if len(seed_values) * 4 * steps_per_phase > 100_000:
        raise ValueError("benchmark exceeds 100000 total observations")

    structural_parameters = PlasticityParameters(
        learning_rate=0.2,
        weight_decay=0.1,
        max_abs_weight=1.0,
        activation_threshold=0.5,
        activation_steps=3,
        prune_threshold=0.08,
        prune_steps=3,
        max_abs_activity=1.0,
        initial_weight=0.05,
    )
    weight_only_parameters = PlasticityParameters(
        learning_rate=0.2,
        weight_decay=0.1,
        max_abs_weight=1.0,
        activation_threshold=0.5,
        activation_steps=3,
        prune_threshold=0.0,
        prune_steps=3,
        max_abs_activity=1.0,
        initial_weight=0.05,
    )
    base_activity_pairs = ((1.0, 1.0), (1.0, -1.0), (0.0, 0.0), (1.0, 1.0))
    names = ("fixed", "weight_only", "structural")
    per_seed = {
        name: {
            "errors": [],
            "active_fractions": [],
            "activations": [],
            "deactivations": [],
            "max_abs": 0.0,
        }
        for name in names
    }

    for seed in seed_values:
        rng = random.Random(seed)
        weight_only = PlasticityState.initial((("pre", "post"),), (0.05,))
        structural = PlasticityState.initial((("pre", "post"),))
        errors = {name: [] for name in names}
        active_counts = {name: 0 for name in names}
        activations = 0
        deactivations = 0

        for base_pre, base_post in base_activity_pairs:
            for _ in range(steps_per_phase):
                pre = max(-1.0, min(1.0, base_pre + rng.uniform(-noise, noise)))
                post = max(-1.0, min(1.0, base_post + rng.uniform(-noise, noise)))
                target = pre * post
                activities = {"pre": pre, "post": post}

                old_structural_active = structural.connections[0].active
                weight_only = step_plasticity(weight_only, activities, weight_only_parameters)
                structural = step_plasticity(structural, activities, structural_parameters)
                structural_edge = structural.connections[0]
                if not old_structural_active and structural_edge.active:
                    activations += 1
                elif old_structural_active and not structural_edge.active:
                    deactivations += 1

                values = {
                    "fixed": (0.05, True),
                    "weight_only": (weight_only.connections[0].weight, weight_only.connections[0].active),
                    "structural": (structural_edge.weight, structural_edge.active),
                }
                for name, (weight, active) in values.items():
                    errors[name].append(abs(weight - target))
                    active_counts[name] += int(active)
                    per_seed[name]["max_abs"] = max(per_seed[name]["max_abs"], abs(weight))

        observations = 4 * steps_per_phase
        for name in names:
            per_seed[name]["errors"].append(_mean(errors[name]))
            per_seed[name]["active_fractions"].append(active_counts[name] / observations)
            per_seed[name]["activations"].append(activations if name == "structural" else 0)
            per_seed[name]["deactivations"].append(deactivations if name == "structural" else 0)

    variants = []
    for name in names:
        metrics = per_seed[name]
        values = (
            _mean(metrics["errors"]),
            _population_stddev(metrics["errors"]),
            _mean(metrics["active_fractions"]),
            _mean(metrics["activations"]),
            _mean(metrics["deactivations"]),
            metrics["max_abs"],
        )
        if not all(math.isfinite(value) for value in values):
            raise RuntimeError("robustness benchmark produced non-finite metrics")
        variants.append(
            PlasticityRobustnessVariant(
                name=name,
                mean_absolute_tracking_error=values[0],
                between_seed_error_stddev=values[1],
                mean_active_step_fraction=values[2],
                mean_activations=values[3],
                mean_deactivations=values[4],
                max_abs_weight_observed=values[5],
            )
        )

    return PlasticityRobustnessReport(
        steps_per_phase=steps_per_phase,
        noise_amplitude=noise,
        seeds=seed_values,
        variants=tuple(variants),
    )
