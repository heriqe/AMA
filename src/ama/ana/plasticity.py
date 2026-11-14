"""Bounded candidate-edge plasticity for ANA v0.5."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from ama.ana.network import Connection


MAX_PLASTICITY_CANDIDATES = 100_000


def _finite_float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    try:
        numeric = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be finite") from error
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    return numeric


def _positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True, slots=True)
class PlasticityParameters:
    """Fixed learning rates, thresholds and bounds for candidate-edge adaptation."""

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
        float_fields = (
            "learning_rate",
            "weight_decay",
            "max_abs_weight",
            "activation_threshold",
            "prune_threshold",
            "max_abs_activity",
            "initial_weight",
        )
        for name in float_fields:
            object.__setattr__(self, name, _finite_float(getattr(self, name), name))

        if self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")
        if not 0.0 <= self.weight_decay <= 1.0:
            raise ValueError("weight_decay must be in [0, 1]")
        if self.max_abs_weight <= 0.0:
            raise ValueError("max_abs_weight must be positive")
        if self.max_abs_activity <= 0.0:
            raise ValueError("max_abs_activity must be positive")
        if not 0.0 < self.activation_threshold <= self.max_abs_activity:
            raise ValueError("activation_threshold must be in (0, max_abs_activity]")
        if not 0.0 <= self.prune_threshold < self.max_abs_weight:
            raise ValueError("prune_threshold must be in [0, max_abs_weight)")
        if self.initial_weight == 0.0 or abs(self.initial_weight) > self.max_abs_weight:
            raise ValueError("initial_weight must be non-zero and within weight bounds")
        _positive_int(self.activation_steps, "activation_steps")
        _positive_int(self.prune_steps, "prune_steps")


@dataclass(frozen=True, slots=True)
class PlasticConnection:
    """One fixed candidate edge and its consecutive-step adaptation counters."""

    source: str
    target: str
    weight: float
    active: bool
    activation_count: int = 0
    prune_count: int = 0

    def __post_init__(self) -> None:
        for name in ("source", "target"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        weight = _finite_float(self.weight, "weight")
        object.__setattr__(self, "weight", weight)
        if not isinstance(self.active, bool):
            raise ValueError("active must be boolean")
        for name in ("activation_count", "prune_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.active:
            if self.activation_count != 0:
                raise ValueError("active connections cannot have an activation counter")
        else:
            if weight != 0.0:
                raise ValueError("inactive connections must have zero weight")
            if self.prune_count != 0:
                raise ValueError("inactive connections cannot have a prune counter")


@dataclass(frozen=True, slots=True)
class PlasticityState:
    """Immutable, ordered and bounded pool of candidate connections."""

    connections: tuple[PlasticConnection, ...]

    def __post_init__(self) -> None:
        try:
            frozen = tuple(self.connections)
        except TypeError as error:
            raise ValueError("connections must be an iterable of PlasticConnection values") from error
        if len(frozen) > MAX_PLASTICITY_CANDIDATES:
            raise ValueError(f"candidate pool exceeds {MAX_PLASTICITY_CANDIDATES} connections")
        if any(not isinstance(item, PlasticConnection) for item in frozen):
            raise ValueError("connections must contain only PlasticConnection values")
        pairs = [(item.source, item.target) for item in frozen]
        if len(pairs) != len(set(pairs)):
            raise ValueError("candidate pairs must be unique")
        object.__setattr__(self, "connections", frozen)

    @classmethod
    def initial(
        cls,
        candidate_pairs: Iterable[tuple[str, str]],
        initial_weights: Iterable[float] | None = None,
    ) -> "PlasticityState":
        try:
            pairs = tuple(candidate_pairs)
        except TypeError as error:
            raise ValueError("candidate_pairs must be iterable") from error
        if len(pairs) > MAX_PLASTICITY_CANDIDATES:
            raise ValueError(f"candidate pool exceeds {MAX_PLASTICITY_CANDIDATES} connections")

        checked_pairs: list[tuple[str, str]] = []
        for pair in pairs:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError("each candidate pair must contain source and target IDs")
            source, target = pair
            if not isinstance(source, str) or not source.strip():
                raise ValueError("candidate source IDs must be non-empty strings")
            if not isinstance(target, str) or not target.strip():
                raise ValueError("candidate target IDs must be non-empty strings")
            checked_pairs.append((source, target))
        if len(checked_pairs) != len(set(checked_pairs)):
            raise ValueError("candidate pairs must be unique")

        if initial_weights is None:
            weights = (0.0,) * len(checked_pairs)
        else:
            try:
                raw_weights = tuple(initial_weights)
            except TypeError as error:
                raise ValueError("initial_weights must be iterable") from error
            if len(raw_weights) != len(checked_pairs):
                raise ValueError("initial_weights must match candidate_pairs")
            weights = tuple(_finite_float(value, "initial weight") for value in raw_weights)

        connections = tuple(
            PlasticConnection(
                source=source,
                target=target,
                weight=weight,
                active=weight != 0.0,
            )
            for (source, target), weight in zip(checked_pairs, weights)
        )
        return cls(connections)

    def active_connections(self) -> tuple[Connection, ...]:
        """Return active v0.2 edges in stable candidate order.

        The caller must explicitly build a new NetworkDefinition; this method
        does not mutate or replace an existing network.
        """
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
    """Apply one deterministic plasticity transition to a fixed candidate pool."""
    if not isinstance(state, PlasticityState):
        raise ValueError("state must be a PlasticityState")
    if not isinstance(parameters, PlasticityParameters):
        raise ValueError("parameters must be PlasticityParameters")
    if not isinstance(activities, Mapping):
        raise ValueError("activities must be a mapping")

    checked: dict[str, float] = {}
    for node_id, value in activities.items():
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("activity node IDs must be non-empty strings")
        numeric = _finite_float(value, "activity")
        if abs(numeric) > parameters.max_abs_activity:
            raise ValueError("activity exceeds max_abs_activity")
        checked[node_id] = numeric

    updated: list[PlasticConnection] = []
    for item in state.connections:
        if item.source not in checked or item.target not in checked:
            raise ValueError("activities must include every candidate endpoint")
        if abs(item.weight) > parameters.max_abs_weight:
            raise ValueError("connection weight exceeds max_abs_weight")
        if item.active:
            if item.activation_count != 0 or item.prune_count >= parameters.prune_steps:
                raise ValueError("active connection counters are inconsistent")
        elif item.prune_count != 0 or item.activation_count >= parameters.activation_steps:
            raise ValueError("inactive connection counters are inconsistent")

        pre = checked[item.source]
        post = checked[item.target]
        coactive = (
            abs(pre) >= parameters.activation_threshold
            and abs(post) >= parameters.activation_threshold
        )

        if item.active:
            product = pre * post
            hebbian = parameters.learning_rate * product
            decay = parameters.weight_decay * item.weight
            if not math.isfinite(product) or not math.isfinite(hebbian) or not math.isfinite(decay):
                raise ValueError("weight update overflowed")
            try:
                raw_weight = math.fsum((item.weight, hebbian, -decay))
            except OverflowError as error:
                raise ValueError("weight update overflowed") from error
            if not math.isfinite(raw_weight):
                raise ValueError("weight update overflowed")
            weight = max(
                -parameters.max_abs_weight,
                min(parameters.max_abs_weight, raw_weight),
            )
            prune_count = item.prune_count + 1 if abs(weight) < parameters.prune_threshold else 0
            if prune_count >= parameters.prune_steps:
                updated.append(
                    PlasticConnection(item.source, item.target, 0.0, False, 0, 0)
                )
            else:
                updated.append(
                    PlasticConnection(item.source, item.target, weight, True, 0, prune_count)
                )
        else:
            activation_count = item.activation_count + 1 if coactive else 0
            if activation_count >= parameters.activation_steps:
                updated.append(
                    PlasticConnection(
                        item.source,
                        item.target,
                        parameters.initial_weight,
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
                        0.0,
                        False,
                        activation_count,
                        0,
                    )
                )

    return PlasticityState(tuple(updated))
