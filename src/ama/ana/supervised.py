"""Small supervised linear readout for ANA v0.4."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ama.ana.unit import Matrix, Vector, _as_vector


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must contain numeric values")
    try:
        converted = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must contain finite values") from error
    if not math.isfinite(converted):
        raise ValueError(f"{name} must contain finite values")
    return converted


@dataclass(frozen=True, slots=True)
class LinearReadoutParameters:
    """Immutable linear model and explicit supervised-learning limits."""

    weights: Matrix
    bias: Vector
    learning_rate: float
    max_abs_parameter: float = 1_000_000.0

    def __post_init__(self) -> None:
        # frozen=True is shallow: snapshot nested inputs so caller-owned lists
        # cannot mutate model parameters after construction.
        try:
            frozen_weights = tuple(tuple(row) for row in self.weights)
            frozen_bias = tuple(self.bias)
        except TypeError as error:
            raise ValueError("weights and bias must be iterable numeric sequences") from error
        object.__setattr__(self, "weights", frozen_weights)
        object.__setattr__(self, "bias", frozen_bias)

        limit = _finite(self.max_abs_parameter, "max_abs_parameter")
        if limit <= 0.0:
            raise ValueError("max_abs_parameter must be positive")
        if _finite(self.learning_rate, "learning_rate") <= 0.0:
            raise ValueError("learning_rate must be positive")
        if not self.weights or not self.bias:
            raise ValueError("weights and bias must not be empty")
        input_size = len(self.weights[0])
        if input_size < 1 or any(len(row) != input_size for row in self.weights):
            raise ValueError("weights must be a non-empty rectangular matrix")
        if len(self.weights) != len(self.bias):
            raise ValueError("weights rows must match bias size")
        for row in self.weights:
            for value in row:
                if abs(_finite(value, "weights")) > limit:
                    raise ValueError("parameter magnitude exceeds configured limit")
        for value in self.bias:
            if abs(_finite(value, "bias")) > limit:
                raise ValueError("parameter magnitude exceeds configured limit")


def predict_readout(parameters: LinearReadoutParameters, features: Vector) -> Vector:
    """Return the linear prediction without changing model parameters."""
    x = _as_vector(features, "features", len(parameters.weights[0]))
    result = tuple(
        math.fsum(weight * value for weight, value in zip(row, x)) + bias
        for row, bias in zip(parameters.weights, parameters.bias)
    )
    return _as_vector(result, "prediction", len(parameters.bias))


def train_readout_step(
    parameters: LinearReadoutParameters,
    features: Vector,
    target: Vector,
) -> LinearReadoutParameters:
    """Apply one deterministic SGD step for mean squared error per output."""
    x = _as_vector(features, "features", len(parameters.weights[0]))
    y = _as_vector(target, "target", len(parameters.bias))
    prediction = predict_readout(parameters, x)
    output_size = len(y)
    errors = tuple(actual - expected for actual, expected in zip(prediction, y))
    scale = 2.0 * parameters.learning_rate / output_size
    weights = tuple(
        tuple(
            weight - scale * error * feature
            for weight, feature in zip(row, x)
        )
        for row, error in zip(parameters.weights, errors)
    )
    bias = tuple(
        value - scale * error
        for value, error in zip(parameters.bias, errors)
    )
    limit = parameters.max_abs_parameter
    if any(
        not math.isfinite(value) or abs(value) > limit
        for row in weights for value in row
    ) or any(not math.isfinite(value) or abs(value) > limit for value in bias):
        raise ValueError("updated parameter magnitude exceeds configured limit")
    return LinearReadoutParameters(
        weights=weights,
        bias=bias,
        learning_rate=parameters.learning_rate,
        max_abs_parameter=limit,
    )
