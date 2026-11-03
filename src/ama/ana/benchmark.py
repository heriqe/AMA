"""Deterministic synthetic benchmark for ANA v0.5 plasticity.

This measures scalar edge-weight tracking under a controlled correlation shift.
It is a mechanism-level proxy, not a neural task or evidence of cognition.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.plasticity import (
    PlasticityParameters,
    PlasticityState,
    step_plasticity,
)


@dataclass(frozen=True, slots=True)
class BenchmarkVariant:
    name: str
    mean_absolute_tracking_error: float
    mean_absolute_weight: float
    active_step_fraction: float
    activations: int
    deactivations: int
    final_weight: float
    final_active: bool


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    steps_per_phase: int
    targets: tuple[float, ...]
    variants: tuple[BenchmarkVariant, ...]


def _clip(value: float, bound: float) -> float:
    return max(-bound, min(bound, value))


def run_plasticity_benchmark(steps_per_phase: int = 40) -> BenchmarkReport:
    """Compare fixed, weight-only, and structural plasticity on four phases.

    Phases have target correlations (+1, -1, 0, +1). Activities are deterministic
    and bounded. The fixed and weight-only baselines start at 0.05. The structural candidate
    starts inactive and receives 0.05 only after its activation delay.
    """
    if isinstance(steps_per_phase, bool) or not isinstance(steps_per_phase, int):
        raise ValueError("steps_per_phase must be an integer")
    if steps_per_phase < 1 or steps_per_phase > 10_000:
        raise ValueError("steps_per_phase must be between 1 and 10000")

    targets = (1.0, -1.0, 0.0, 1.0)
    activities = ((1.0, 1.0), (1.0, -1.0), (0.0, 0.0), (1.0, 1.0))
    parameters = PlasticityParameters(
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

    fixed_weight = 0.05
    weight_only = 0.05
    structural = PlasticityState.initial((("pre", "post"),))
    accumulators = {
        "fixed": {"error": 0.0, "magnitude": 0.0, "active": 0, "count": 0},
        "weight_only": {"error": 0.0, "magnitude": 0.0, "active": 0, "count": 0},
        "structural": {"error": 0.0, "magnitude": 0.0, "active": 0, "count": 0},
    }
    transitions = {"structural": {"activate": 0, "deactivate": 0}}

    for target, (pre, post) in zip(targets, activities):
        for _ in range(steps_per_phase):
            old_active = structural.connections[0].active

            # Same bounded Hebbian update as v0.5, but no topology changes.
            weight_only = _clip(
                weight_only
                + parameters.learning_rate * pre * post
                - parameters.weight_decay * weight_only,
                parameters.max_abs_weight,
            )
            structural = step_plasticity(
                structural,
                {"pre": pre, "post": post},
                parameters,
            )
            edge = structural.connections[0]
            if not old_active and edge.active:
                transitions["structural"]["activate"] += 1
            elif old_active and not edge.active:
                transitions["structural"]["deactivate"] += 1

            values = {
                "fixed": (fixed_weight, True),
                "weight_only": (weight_only, True),
                "structural": (edge.weight, edge.active),
            }
            for name, (weight, active) in values.items():
                metrics = accumulators[name]
                metrics["error"] += abs(weight - target)
                metrics["magnitude"] += abs(weight)
                metrics["active"] += int(active)
                metrics["count"] += 1

    variants = []
    for name in ("fixed", "weight_only", "structural"):
        metrics = accumulators[name]
        count = metrics["count"]
        if count == 0:
            raise RuntimeError("benchmark produced no observations")
        if not all(math.isfinite(float(metrics[key])) for key in ("error", "magnitude")):
            raise RuntimeError("benchmark produced non-finite metrics")
        if name == "structural":
            final_weight = structural.connections[0].weight
            final_active = structural.connections[0].active
            activations = transitions[name]["activate"]
            deactivations = transitions[name]["deactivate"]
        else:
            final_weight = fixed_weight if name == "fixed" else weight_only
            final_active = True
            activations = 0
            deactivations = 0
        variants.append(
            BenchmarkVariant(
                name=name,
                mean_absolute_tracking_error=metrics["error"] / count,
                mean_absolute_weight=metrics["magnitude"] / count,
                active_step_fraction=metrics["active"] / count,
                activations=activations,
                deactivations=deactivations,
                final_weight=final_weight,
                final_active=final_active,
            )
        )

    return BenchmarkReport(
        steps_per_phase=steps_per_phase,
        targets=targets,
        variants=tuple(variants),
    )



@dataclass(frozen=True, slots=True)
class NoiseBenchmarkVariant:
    """Aggregate result for one benchmark variant across deterministic seeds."""

    name: str
    mean_tracking_error: float
    tracking_error_stddev: float
    mean_active_step_fraction: float
    mean_activations: float
    mean_deactivations: float


@dataclass(frozen=True, slots=True)
class NoiseBenchmarkReport:
    """Aggregate report for a controlled-noise multi-seed experiment."""

    seeds: tuple[int, ...]
    steps_per_phase: int
    noise_amplitude: float
    variants: tuple[NoiseBenchmarkVariant, ...]


def run_noise_robustness_benchmark(
    seeds: tuple[int, ...] = (7, 17, 27, 37, 47),
    steps_per_phase: int = 40,
    noise_amplitude: float = 0.1,
) -> NoiseBenchmarkReport:
    """Compare plasticity variants under bounded Gaussian activity noise.

    Every variant receives exactly the same noisy activity sequence for a
    given seed. Seeds and noise amplitude are explicit so runs are repeatable.
    The target remains the ideal phase correlation (+1, -1, 0, +1); reported
    error is therefore a tracking proxy under noisy observations.
    """
    import random

    if not isinstance(seeds, tuple) or not seeds:
        raise ValueError("seeds must be a non-empty tuple of integers")
    if len(seeds) > 100:
        raise ValueError("at most 100 seeds are supported")
    if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        raise ValueError("seeds must contain integers")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique")
    if isinstance(steps_per_phase, bool) or not isinstance(steps_per_phase, int):
        raise ValueError("steps_per_phase must be an integer")
    if steps_per_phase < 1 or steps_per_phase > 10_000:
        raise ValueError("steps_per_phase must be between 1 and 10000")
    if isinstance(noise_amplitude, bool) or not isinstance(noise_amplitude, (int, float)):
        raise ValueError("noise_amplitude must be numeric")
    noise_amplitude = float(noise_amplitude)
    if not math.isfinite(noise_amplitude) or not 0.0 <= noise_amplitude <= 0.5:
        raise ValueError("noise_amplitude must be finite and in [0, 0.5]")

    targets = (1.0, -1.0, 0.0, 1.0)
    base_activities = ((1.0, 1.0), (1.0, -1.0), (0.0, 0.0), (1.0, 1.0))
    parameters = PlasticityParameters(
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
    per_seed: dict[str, list[tuple[float, float, int, int]]] = {
        name: [] for name in ("fixed", "weight_only", "structural")
    }

    for seed in seeds:
        rng = random.Random(seed)
        fixed_weight = 0.05
        weight_only = 0.05
        structural = PlasticityState.initial((("pre", "post"),))
        metrics = {
            name: {"error": 0.0, "active": 0, "count": 0}
            for name in per_seed
        }
        activations = 0
        deactivations = 0

        for target, (base_pre, base_post) in zip(targets, base_activities):
            for _ in range(steps_per_phase):
                pre = max(
                    -1.0,
                    min(1.0, base_pre + rng.gauss(0.0, noise_amplitude)),
                )
                post = max(
                    -1.0,
                    min(1.0, base_post + rng.gauss(0.0, noise_amplitude)),
                )
                old_active = structural.connections[0].active
                weight_only = _clip(
                    weight_only
                    + parameters.learning_rate * pre * post
                    - parameters.weight_decay * weight_only,
                    parameters.max_abs_weight,
                )
                structural = step_plasticity(
                    structural,
                    {"pre": pre, "post": post},
                    parameters,
                )
                edge = structural.connections[0]
                if not old_active and edge.active:
                    activations += 1
                elif old_active and not edge.active:
                    deactivations += 1

                values = {
                    "fixed": (fixed_weight, True),
                    "weight_only": (weight_only, True),
                    "structural": (edge.weight, edge.active),
                }
                for name, (weight, active) in values.items():
                    metrics[name]["error"] += abs(weight - target)
                    metrics[name]["active"] += int(active)
                    metrics[name]["count"] += 1

        for name, item in metrics.items():
            count = item["count"]
            per_seed[name].append(
                (
                    item["error"] / count,
                    item["active"] / count,
                    activations if name == "structural" else 0,
                    deactivations if name == "structural" else 0,
                )
            )

    variants = []
    for name, records in per_seed.items():
        errors = [record[0] for record in records]
        mean_error = sum(errors) / len(errors)
        variance = sum((value - mean_error) ** 2 for value in errors) / len(errors)
        variants.append(
            NoiseBenchmarkVariant(
                name=name,
                mean_tracking_error=mean_error,
                tracking_error_stddev=math.sqrt(variance),
                mean_active_step_fraction=sum(r[1] for r in records) / len(records),
                mean_activations=sum(r[2] for r in records) / len(records),
                mean_deactivations=sum(r[3] for r in records) / len(records),
            )
        )

    return NoiseBenchmarkReport(
        seeds=seeds,
        steps_per_phase=steps_per_phase,
        noise_amplitude=noise_amplitude,
        variants=tuple(variants),
    )
