"""Bounded multi-timescale memory and context for ANA v0.3."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Vector, _as_vector


@dataclass(frozen=True, slots=True)
class MultiScaleMemoryParameters:
    """Fixed decay rates and contribution weights for temporal traces."""

    scale_ids: tuple[str, ...]
    retention: tuple[float, ...]
    context_weights: tuple[float, ...]

    def __post_init__(self) -> None:
        count = len(self.scale_ids)
        if count < 2:
            raise ValueError("at least two memory scales are required")
        if len(set(self.scale_ids)) != count or any(
            not isinstance(item, str) or not item.strip() for item in self.scale_ids
        ):
            raise ValueError("scale IDs must be unique non-empty strings")
        if len(self.retention) != count or len(self.context_weights) != count:
            raise ValueError("scale IDs, retention and context weights must align")

        for value in self.retention:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("retention values must be numeric")
            if not math.isfinite(value) or not 0.0 <= value < 1.0:
                raise ValueError("retention values must be finite and in [0, 1)")
        if any(a >= b for a, b in zip(self.retention, self.retention[1:])):
            raise ValueError("retention values must increase from fast to slow scales")

        for value in self.context_weights:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("context weights must be numeric")
            if not math.isfinite(value) or value < 0.0:
                raise ValueError("context weights must be finite and non-negative")
        if sum(self.context_weights) <= 0.0:
            raise ValueError("at least one context weight must be positive")


@dataclass(frozen=True, slots=True)
class MultiScaleMemoryState:
    """One exponentially decaying trace vector per configured time scale."""

    traces: tuple[Vector, ...]

    @classmethod
    def initial(
        cls, parameters: MultiScaleMemoryParameters, signal_size: int
    ) -> "MultiScaleMemoryState":
        if isinstance(signal_size, bool) or not isinstance(signal_size, int) or signal_size < 1:
            raise ValueError("signal_size must be a positive integer")
        zero = (0.0,) * signal_size
        return cls(traces=tuple(zero for _ in parameters.scale_ids))


@dataclass(frozen=True, slots=True)
class MultiScaleMemoryResult:
    """Updated temporal traces and their combined context vector."""

    state: MultiScaleMemoryState
    context: Vector


def step_multiscale_memory(
    state: MultiScaleMemoryState,
    signal: Vector,
    parameters: MultiScaleMemoryParameters,
) -> MultiScaleMemoryResult:
    """Update all timescales from one signal and combine a deterministic context.

    Each trace is an exponential moving average:
        z_k(t) = rho_k * z_k(t-1) + (1-rho_k) * signal(t)

    The context is the normalized weighted sum of all updated traces.
    """
    if len(state.traces) != len(parameters.scale_ids):
        raise ValueError("state must contain one trace per configured scale")
    if not state.traces:
        raise ValueError("state must contain at least one trace")

    signal_size = len(signal)
    current_signal = _as_vector(signal, "signal", signal_size)
    if signal_size < 1:
        raise ValueError("signal must not be empty")

    updated: list[Vector] = []
    for index, (previous, retention) in enumerate(
        zip(state.traces, parameters.retention)
    ):
        previous_trace = _as_vector(
            previous, f"state.traces[{index}]", signal_size
        )
        updated.append(
            tuple(
                retention * old + (1.0 - retention) * current
                for old, current in zip(previous_trace, current_signal)
            )
        )

    weight_total = sum(parameters.context_weights)
    context = tuple(
        sum(
            weight * trace[dimension]
            for weight, trace in zip(parameters.context_weights, updated)
        )
        / weight_total
        for dimension in range(signal_size)
    )
    return MultiScaleMemoryResult(
        state=MultiScaleMemoryState(traces=tuple(updated)),
        context=context,
    )
