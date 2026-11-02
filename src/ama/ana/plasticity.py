"""Bounded dynamic-connection plasticity for ANA v0.5."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

from ama.ana.network import Connection


@dataclass(frozen=True, slots=True)
class PlasticityParameters:
    """Fixed thresholds and bounds for deterministic structural adaptation."""

    learning_rate: float = 0.02
    weight_decay: float = 0.01
    max_abs_weight: float = 1.0
    activation_threshold: float = 0.5
    activation_steps: int = 3
    prune_threshold: float = 0.02
    prune_steps: int = 5
    max_abs_activity: float = 1.0
    initial_weight: float = 0.05

    def __post_init__(self) -> None:
        for name in (
            "learning_rate",
            "weight_decay",
            "max_abs_weight",
            "activation_threshold",
            "prune_threshold",
            "max_abs_activity",
            "initial_weight",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")
        if self.weight_decay < 0.0:
            raise ValueError("weight_decay must be non-negative")
        if self.max_abs_weight <= 0.0:
            raise ValueError("max_abs_weight must be positive")
        if not 0.0 <= self.activation_threshold <= self.max_abs_activity:
            raise ValueError("activation_threshold is outside activity bounds")
        if self.prune_threshold < 0.0 or self.prune_threshold >= self.max_abs_weight:
            raise ValueError("prune_threshold must be in [0, max_abs_weight)")
        if self.max_abs_activity <= 0.0:
            raise ValueError("max_abs_activity must be positive")
        if self.activation_steps < 1 or self.prune_steps < 1:
            raise ValueError("activation_steps and prune_steps must be positive")
        if not 0.0 < abs(self.initial_weight) <= self.max_abs_weight:
            raise ValueError("initial_weight must be non-zero and within weight bounds")


@dataclass(frozen=True, slots=True)
class PlasticConnection:
    """Candidate directed connection and its structural adaptation counters."""

    source: str
    target: str
    weight: float
    active: bool
    activation_count: int = 0
    prune_count: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("connection source must be a non-empty string")
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("connection target must be a non-empty string")
        if self.source == self.target:
            raise ValueError("self-connections are not supported in v0.5")
        if isinstance(self.weight, bool) or not isinstance(self.weight, (int, float)):
            raise ValueError("connection weight must be numeric")
        if not math.isfinite(self.weight):
            raise ValueError("connection weight must be finite")
        if not isinstance(self.active, bool):
            raise ValueError("active must be boolean")
        if self.activation_count < 0 or self.prune_count < 0:
            raise ValueError("adaptation counters must be non-negative")


@dataclass(frozen=True, slots=True)
class PlasticityState:
    """Immutable candidate pool; inactive candidates can become active later."""

    connections: tuple[PlasticConnection, ...]

    @classmethod
    def initial(
        cls,
        candidate_pairs: tuple[tuple[str, str], ...],
        initial_weights: tuple[float, ...] | None = None,
    ) -> "PlasticityState":
        if initial_weights is not None and len(initial_weights) != len(candidate_pairs):
            raise ValueError("initial_weights must match candidate_pairs")
        weights = initial_weights or (0.0,) * len(candidate_pairs)
        seen: set[tuple[str, str]] = set()
        items: list[PlasticConnection] = []
        for (source, target), weight in zip(candidate_pairs, weights):
            pair = (source, target)
            if pair in seen:
                raise ValueError("candidate pairs must be unique")
            seen.add(pair)
            items.append(
                PlasticConnection(
                    source=source,
                    target=target,
                    weight=weight,
                    active=weight != 0.0,
                )
            )
        return cls(tuple(items))

    def active_connections(self) -> tuple[Connection, ...]:
        """Return active edges in stable candidate order for network execution."""
        return tuple(
            Connection(item.source, item.target, item.weight)
            for item in self.connections
            if item.active
        )


def step_plasticity(
    state: PlasticityState,
    activities: Mapping[str, float],
    parameters: PlasticityParameters,
) -> PlasticityState:
    """Update candidate edges from one activity snapshot.

    Active edges use a bounded Hebbian term with weight decay. Inactive edges
    activate only after repeated co-activation. Active edges are pruned only
    after their magnitude remains below the prune threshold for several steps.
    The candidate pool itself is fixed and must be explicitly supplied by the
    caller; this function never invents arbitrary node pairs.
    """
    if not isinstance(activities, Mapping):
        raise ValueError("activities must be a mapping")
    checked: dict[str, float] = {}
    for node_id, value in activities.items():
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("activity node IDs must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("activities must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError("activities must be finite")
        if abs(numeric) > parameters.max_abs_activity:
            raise ValueError("activity exceeds max_abs_activity")
        checked[node_id] = numeric

    pairs: set[tuple[str, str]] = set()
    updated: list[PlasticConnection] = []
    for item in state.connections:
        pair = (item.source, item.target)
        if pair in pairs:
            raise ValueError("plasticity state contains duplicate candidates")
        pairs.add(pair)
        if item.source not in checked or item.target not in checked:
            raise ValueError("activities must include every candidate endpoint")
        if abs(item.weight) > parameters.max_abs_weight:
            raise ValueError("connection weight exceeds max_abs_weight")

        pre = checked[item.source]
        post = checked[item.target]
        coactive = (
            abs(pre) >= parameters.activation_threshold
            and abs(post) >= parameters.activation_threshold
        )

        if item.active:
            raw_weight = (
                item.weight
                + parameters.learning_rate * pre * post
                - parameters.weight_decay * item.weight
            )
            weight = max(
                -parameters.max_abs_weight,
                min(parameters.max_abs_weight, raw_weight),
            )
            prune_count = item.prune_count + 1 if abs(weight) < parameters.prune_threshold else 0
            if prune_count >= parameters.prune_steps:
                updated.append(
                    PlasticConnection(
                        item.source,
                        item.target,
                        0.0,
                        False,
                        0,
                        0,
                    )
                )
            else:
                updated.append(
                    PlasticConnection(
                        item.source,
                        item.target,
                        weight,
                        True,
                        0,
                        prune_count,
                    )
                )
        else:
            activation_count = item.activation_count + 1 if coactive else 0
            if activation_count >= parameters.activation_steps:
                weight = max(
                    -parameters.max_abs_weight,
                    min(parameters.max_abs_weight, parameters.initial_weight),
                )
                updated.append(
                    PlasticConnection(
                        item.source,
                        item.target,
                        weight,
                        True,
                        0,
                        0,
                    )
                )
            else:
                updated.append(
                    PlasticConnection(
                        item.source,
                        item.target,
                        item.weight,
                        False,
                        activation_count,
                        0,
                    )
                )
    return PlasticityState(tuple(updated))
