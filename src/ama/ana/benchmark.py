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
