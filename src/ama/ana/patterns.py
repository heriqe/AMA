"""Bounded incremental prototype discovery for ANA v0.4."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Vector, _as_vector


@dataclass(frozen=True, slots=True)
class PatternDiscoveryParameters:
    """Fixed vector dimension, prototype capacity and squared-distance threshold."""

    feature_size: int
    max_prototypes: int
    squared_distance_threshold: float

    def __post_init__(self) -> None:
        if isinstance(self.feature_size, bool) or not isinstance(self.feature_size, int) or self.feature_size < 1:
            raise ValueError("feature_size must be a positive integer")
        if isinstance(self.max_prototypes, bool) or not isinstance(self.max_prototypes, int) or self.max_prototypes < 1:
            raise ValueError("max_prototypes must be a positive integer")
        value = self.squared_distance_threshold
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("squared_distance_threshold must be finite and non-negative")
        try:
            threshold = float(value)
        except OverflowError as error:
            raise ValueError("squared_distance_threshold must be finite and non-negative") from error
        if not math.isfinite(threshold) or threshold < 0.0:
            raise ValueError("squared_distance_threshold must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class PatternPrototype:
    """One online centroid with a stable sequential identifier."""

    prototype_id: int
    centroid: Vector
    count: int

    def __post_init__(self) -> None:
        # Keep the centroid independent from mutable caller-owned sequences.
        try:
            frozen_centroid = tuple(self.centroid)
        except TypeError as error:
            raise ValueError("centroid must be an iterable numeric vector") from error
        object.__setattr__(self, "centroid", frozen_centroid)


@dataclass(frozen=True, slots=True)
class PatternDiscoveryState:
    """Immutable bounded collection of discovered prototypes."""

    prototypes: tuple[PatternPrototype, ...] = ()
    next_id: int = 0

    def __post_init__(self) -> None:
        try:
            frozen_prototypes = tuple(self.prototypes)
        except TypeError as error:
            raise ValueError("prototypes must be an iterable of PatternPrototype values") from error
        if any(not isinstance(item, PatternPrototype) for item in frozen_prototypes):
            raise ValueError("prototypes must contain only PatternPrototype values")
        object.__setattr__(self, "prototypes", frozen_prototypes)


@dataclass(frozen=True, slots=True)
class PatternAssignment:
    """Updated state and the observation's deterministic prototype assignment."""

    state: PatternDiscoveryState
    prototype_id: int
    distance_squared: float
    created: bool


def assign_pattern(
    state: PatternDiscoveryState,
    observation: Vector,
    parameters: PatternDiscoveryParameters,
) -> PatternAssignment:
    """Assign an observation to its nearest prototype or create one if allowed."""
    x = _as_vector(observation, "observation", parameters.feature_size)
    if len(state.prototypes) > parameters.max_prototypes:
        raise ValueError("state exceeds configured prototype capacity")

    ids = [item.prototype_id for item in state.prototypes]
    if any(
        isinstance(item, bool) or not isinstance(item, int) or item < 0
        for item in ids
    ):
        raise ValueError("prototype IDs must be unique non-negative integers")
    if len(ids) != len(set(ids)):
        raise ValueError("prototype IDs must be unique non-negative integers")
    if any(
        isinstance(item.count, bool)
        or not isinstance(item.count, int)
        or item.count < 1
        for item in state.prototypes
    ):
        raise ValueError("prototype counts must be positive integers")
    for item in state.prototypes:
        _as_vector(item.centroid, "prototype centroid", parameters.feature_size)

    if isinstance(state.next_id, bool) or not isinstance(state.next_id, int) or state.next_id < 0:
        raise ValueError("next_id must be a non-negative integer")
    if ids and state.next_id <= max(ids):
        raise ValueError("next_id must exceed all existing prototype IDs")

    try:
        distances = tuple(
            (
                math.fsum(
                    (value - center) ** 2
                    for value, center in zip(x, item.centroid)
                ),
                item.prototype_id,
            )
            for item in state.prototypes
        )
    except OverflowError as error:
        raise ValueError("distance calculation overflowed") from error
    if any(not math.isfinite(distance) for distance, _ in distances):
        raise ValueError("distance calculation overflowed")
    if not distances:
        return _create(state, x)

    distance, selected_id = min(distances, key=lambda pair: (pair[0], pair[1]))
    threshold = float(parameters.squared_distance_threshold)
    if distance > threshold and len(state.prototypes) < parameters.max_prototypes:
        return _create(state, x)

    updated = []
    for item in state.prototypes:
        if item.prototype_id == selected_id:
            new_count = item.count + 1
            centroid = tuple(
                center + (value - center) / new_count
                for center, value in zip(item.centroid, x)
            )
            centroid = _as_vector(
                centroid, "updated centroid", parameters.feature_size
            )
            updated.append(PatternPrototype(item.prototype_id, centroid, new_count))
        else:
            updated.append(item)

    return PatternAssignment(
        state=PatternDiscoveryState(tuple(updated), state.next_id),
        prototype_id=selected_id,
        distance_squared=distance,
        created=False,
    )


def _create(
    state: PatternDiscoveryState,
    observation: Vector,
) -> PatternAssignment:
    prototype_id = state.next_id
    prototype = PatternPrototype(prototype_id, observation, 1)
    updated = PatternDiscoveryState(
        state.prototypes + (prototype,),
        prototype_id + 1,
    )
    return PatternAssignment(updated, prototype_id, 0.0, True)
