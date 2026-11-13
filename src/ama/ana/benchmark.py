"""Deterministic mechanism-level benchmark for ANA v0.5 plasticity."""

from __future__ import annotations

import math
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


def run_plasticity_benchmark(steps_per_phase: int = 40) -> PlasticityBenchmarkReport:
    """Compare fixed, weight-only and structural variants on four deterministic phases.

    The target is the product of two bounded activities. Tracking error is a
    mechanism-level proxy, not prediction error or a measure of cognition.
    """
    if isinstance(steps_per_phase, bool) or not isinstance(steps_per_phase, int):
        raise ValueError("steps_per_phase must be an integer")
    if not 1 <= steps_per_phase <= 10_000:
        raise ValueError("steps_per_phase must be between 1 and 10000")

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
