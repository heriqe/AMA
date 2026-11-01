"""Experimental single-unit transition for the ANA v0.1 specification."""

from __future__ import annotations

import math
from dataclasses import dataclass


Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]


def _as_vector(values: tuple[float, ...], name: str, size: int) -> Vector:
    try:
        if len(values) != size:
            raise ValueError(f"{name} must have length {size}")
    except TypeError as error:
        raise ValueError(f"{name} must be a numeric vector") from error
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        raise ValueError(f"{name} must contain only numeric values")
    result = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain only finite numbers")
    return result


def _validate_matrix(matrix: Matrix, name: str, rows: int, columns: int) -> None:
    try:
        valid_shape = len(matrix) == rows and all(len(row) == columns for row in matrix)
    except TypeError as error:
        raise ValueError(f"{name} must be a numeric matrix") from error
    if not valid_shape:
        raise ValueError(f"{name} must have shape ({rows}, {columns})")
    values = (value for row in matrix for value in row)
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must contain only numeric values")
        if not math.isfinite(value):
            raise ValueError(f"{name} must contain only finite numbers")


def _matvec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum(weight * value for weight, value in zip(row, vector)) for row in matrix)


def _sum_vectors(*vectors: Vector) -> Vector:
    return tuple(sum(values) for values in zip(*vectors))


def _tanh(vector: Vector) -> Vector:
    return tuple(math.tanh(value) for value in vector)


def _hadamard(left: Vector, right: Vector) -> Vector:
    return tuple(a * b for a, b in zip(left, right))


@dataclass(frozen=True, slots=True)
class NeuralUnitInput:
    """External and relational signals for one discrete time step."""

    external: Vector
    relational: Vector


@dataclass(frozen=True, slots=True)
class NeuralUnitState:
    """Dynamic state carried by one neural unit."""

    x: Vector
    m: Vector
    c: Vector
    g: Vector
    y: Vector

    @classmethod
    def initial(cls, parameters: "NeuralUnitParameters") -> "NeuralUnitState":
        """Create the reference initial state x=m=c=y=0 and g=1."""
        zero = (0.0,) * parameters.internal_size
        return cls(
            x=zero,
            m=zero,
            c=zero,
            g=(1.0,) * parameters.internal_size,
            y=(0.0,) * parameters.output_size,
        )


@dataclass(frozen=True, slots=True)
class NeuralUnitParameters:
    """Fixed matrices and scalars defining one ANA v0.1 unit."""

    input_size: int
    relation_size: int
    internal_size: int
    output_size: int

    w_xx: Matrix
    w_xm: Matrix
    w_xc: Matrix
    w_xu: Matrix
    w_xr: Matrix
    b_x: Vector

    w_cc: Matrix
    w_cx: Matrix
    w_cr: Matrix
    b_c: Vector

    w_gx: Matrix
    w_gc: Matrix
    w_gm: Matrix
    b_g: Vector

    w_mx: Matrix
    w_mc: Matrix
    w_mu: Matrix
    b_m: Vector

    w_yx: Matrix
    w_ym: Matrix
    w_yc: Matrix
    b_y: Vector

    rho: float = 0.9
    eta: float = 0.1
    gamma: float = 0.5

    def __post_init__(self) -> None:
        dimensions = (
            self.input_size,
            self.relation_size,
            self.internal_size,
            self.output_size,
        )
        if any(
            isinstance(size, bool) or not isinstance(size, int) or size < 1
            for size in dimensions
        ):
            raise ValueError("all dimensions must be positive integers")

        d, du, dr, dy = (
            self.internal_size,
            self.input_size,
            self.relation_size,
            self.output_size,
        )
        shapes = {
            "w_xx": (self.w_xx, d, d),
            "w_xm": (self.w_xm, d, d),
            "w_xc": (self.w_xc, d, d),
            "w_xu": (self.w_xu, d, du),
            "w_xr": (self.w_xr, d, dr),
            "w_cc": (self.w_cc, d, d),
            "w_cx": (self.w_cx, d, d),
            "w_cr": (self.w_cr, d, dr),
            "w_gx": (self.w_gx, d, d),
            "w_gc": (self.w_gc, d, d),
            "w_gm": (self.w_gm, d, d),
            "w_mx": (self.w_mx, d, d),
            "w_mc": (self.w_mc, d, d),
            "w_mu": (self.w_mu, d, du),
            "w_yx": (self.w_yx, dy, d),
            "w_ym": (self.w_ym, dy, d),
            "w_yc": (self.w_yc, dy, d),
        }
        for name, (matrix, rows, columns) in shapes.items():
            _validate_matrix(matrix, name, rows, columns)

        for name in ("b_x", "b_c", "b_g", "b_m"):
            _as_vector(getattr(self, name), name, d)
        _as_vector(self.b_y, "b_y", dy)

        for name, value in (
            ("rho", self.rho),
            ("eta", self.eta),
            ("gamma", self.gamma),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0.0 <= self.rho < 1.0:
            raise ValueError("rho must satisfy 0 <= rho < 1")
        if self.eta < 0.0:
            raise ValueError("eta must be non-negative")
        if not 0.0 <= self.gamma <= 1.0:
            raise ValueError("gamma must satisfy 0 <= gamma <= 1")

    @classmethod
    def zeros(
        cls,
        *,
        input_size: int,
        relation_size: int,
        internal_size: int,
        output_size: int,
        rho: float = 0.9,
        eta: float = 0.1,
        gamma: float = 0.5,
    ) -> "NeuralUnitParameters":
        """Build a zero-weight parameter set for deterministic tests."""
        d, du, dr, dy = internal_size, input_size, relation_size, output_size

        def matrix(rows: int, columns: int) -> Matrix:
            return tuple((0.0,) * columns for _ in range(rows))

        zero = (0.0,) * d
        return cls(
            input_size=du,
            relation_size=dr,
            internal_size=d,
            output_size=dy,
            w_xx=matrix(d, d),
            w_xm=matrix(d, d),
            w_xc=matrix(d, d),
            w_xu=matrix(d, du),
            w_xr=matrix(d, dr),
            b_x=zero,
            w_cc=matrix(d, d),
            w_cx=matrix(d, d),
            w_cr=matrix(d, dr),
            b_c=zero,
            w_gx=matrix(d, d),
            w_gc=matrix(d, d),
            w_gm=matrix(d, d),
            b_g=zero,
            w_mx=matrix(d, d),
            w_mc=matrix(d, d),
            w_mu=matrix(d, du),
            b_m=zero,
            w_yx=matrix(dy, d),
            w_ym=matrix(dy, d),
            w_yc=matrix(dy, d),
            b_y=(0.0,) * dy,
            rho=rho,
            eta=eta,
            gamma=gamma,
        )


def step(
    state: NeuralUnitState,
    signals: NeuralUnitInput,
    parameters: NeuralUnitParameters,
) -> NeuralUnitState:
    """Advance one unit by one time step without mutating its inputs."""
    d = parameters.internal_size
    x_prev = _as_vector(state.x, "state.x", d)
    m_prev = _as_vector(state.m, "state.m", d)
    c_prev = _as_vector(state.c, "state.c", d)
    g_prev = _as_vector(state.g, "state.g", d)
    _as_vector(state.y, "state.y", parameters.output_size)
    if any(value < 0.0 or value > 2.0 for value in g_prev):
        raise ValueError("state.g values must be within [0, 2]")
    external = _as_vector(signals.external, "signals.external", parameters.input_size)
    relational = _as_vector(
        signals.relational, "signals.relational", parameters.relation_size
    )

    px = _sum_vectors(
        _matvec(parameters.w_xx, x_prev),
        _matvec(parameters.w_xm, m_prev),
        _matvec(parameters.w_xc, c_prev),
        _matvec(parameters.w_xu, external),
        _matvec(parameters.w_xr, relational),
        parameters.b_x,
    )
    x = _tanh(_hadamard(g_prev, px))

    c = _tanh(
        _sum_vectors(
            _matvec(parameters.w_cc, c_prev),
            _matvec(parameters.w_cx, x),
            _matvec(parameters.w_cr, relational),
            parameters.b_c,
        )
    )

    modulation_signal = _sum_vectors(
        _matvec(parameters.w_gx, x),
        _matvec(parameters.w_gc, c),
        _matvec(parameters.w_gm, m_prev),
        parameters.b_g,
    )
    g = tuple(1.0 + parameters.gamma * value for value in _tanh(modulation_signal))

    memory_candidate = _tanh(
        _sum_vectors(
            _matvec(parameters.w_mx, x),
            _matvec(parameters.w_mc, c),
            _matvec(parameters.w_mu, external),
            parameters.b_m,
        )
    )
    m = tuple(
        parameters.rho * previous + parameters.eta * gain * candidate
        for previous, gain, candidate in zip(m_prev, g, memory_candidate)
    )

    y = _tanh(
        _sum_vectors(
            _matvec(parameters.w_yx, x),
            _matvec(parameters.w_ym, m),
            _matvec(parameters.w_yc, c),
            parameters.b_y,
        )
    )

    return NeuralUnitState(x=x, m=m, c=c, g=g, y=y)
