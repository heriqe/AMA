"""Reward-modulated linear action preferences for ANA v0.4."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Matrix, Vector, _as_vector


def _finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


@dataclass(frozen=True, slots=True)
class RewardLearningParameters:
    """Fixed dimensions, learning rates and numerical safety limits."""

    action_count: int
    feature_size: int
    learning_rate: float
    baseline_rate: float
    eligibility_decay: float
    max_abs_weight: float = 1_000_000.0
    max_abs_eligibility: float = 1_000_000.0

    def __post_init__(self) -> None:
        if isinstance(self.action_count, bool) or not isinstance(self.action_count, int) or self.action_count < 1:
            raise ValueError("action_count must be a positive integer")
        if isinstance(self.feature_size, bool) or not isinstance(self.feature_size, int) or self.feature_size < 1:
            raise ValueError("feature_size must be a positive integer")
        if not _finite_number(self.learning_rate) or self.learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")
        if not _finite_number(self.baseline_rate) or not 0 < self.baseline_rate <= 1:
            raise ValueError("baseline_rate must be finite and in (0, 1]")
        if not _finite_number(self.eligibility_decay) or not 0 <= self.eligibility_decay < 1:
            raise ValueError("eligibility_decay must be finite and in [0, 1)")
        if not _finite_number(self.max_abs_weight) or self.max_abs_weight <= 0:
            raise ValueError("max_abs_weight must be finite and positive")
        if not _finite_number(self.max_abs_eligibility) or self.max_abs_eligibility <= 0:
            raise ValueError("max_abs_eligibility must be finite and positive")
