from dataclasses import replace
import math

import pytest

from ama.ana.unit import NeuralUnitInput, NeuralUnitParameters, NeuralUnitState, step


def params(**kwargs):
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=1
    )
    return replace(base, **kwargs)


def test_zero_parameters_produce_zero_activity_and_neutral_modulation():
    p = params()
    initial = NeuralUnitState.initial(p)

    result = step(initial, NeuralUnitInput((1.0,), (-1.0,)), p)

    assert result.x == (0.0,)
    assert result.m == (0.0,)
    assert result.c == (0.0,)
    assert result.g == (1.0,)
    assert result.y == (0.0,)


def test_external_input_affects_state_and_output():
    p = params(w_xu=((1.0,),), w_yx=((1.0,),))
    result = step(
        NeuralUnitState.initial(p), NeuralUnitInput((1.0,), (0.0,)), p
    )

    assert result.x[0] == pytest.approx(math.tanh(1.0))
    assert result.y[0] == pytest.approx(math.tanh(result.x[0]))


def test_relational_signal_updates_context():
    p = params(w_cr=((1.0,),))
    result = step(
        NeuralUnitState.initial(p), NeuralUnitInput((0.0,), (0.75,)), p
    )

    assert result.c[0] == pytest.approx(math.tanh(0.75))


def test_memory_retention_uses_rho_when_candidate_is_zero():
    p = params(rho=0.5, eta=0.0)
    previous = NeuralUnitState(x=(0.0,), m=(2.0,), c=(0.0,), g=(1.0,), y=(0.0,))

    result = step(previous, NeuralUnitInput((0.0,), (0.0,)), p)

    assert result.m == pytest.approx((1.0,))


def test_memory_candidate_is_modulated():
    p = params(w_mu=((1.0,),), eta=0.2, rho=0.0, gamma=0.0)
    result = step(
        NeuralUnitState.initial(p), NeuralUnitInput((1.0,), (0.0,)), p
    )

    assert result.m[0] == pytest.approx(0.2 * math.tanh(1.0))


def test_parameter_shapes_are_validated():
    with pytest.raises(ValueError, match="w_xu"):
        params(w_xu=((1.0, 2.0),))


def test_invalid_modulation_range_is_rejected():
    with pytest.raises(ValueError, match="gamma"):
        params(gamma=1.5)


def test_non_finite_input_is_rejected():
    p = params()
    with pytest.raises(ValueError, match="finite"):
        step(
            NeuralUnitState.initial(p),
            NeuralUnitInput((float("nan"),), (0.0,)),
            p,
        )


def test_transition_does_not_mutate_previous_state():
    p = params(w_xu=((1.0,),))
    previous = NeuralUnitState.initial(p)
    snapshot = previous

    step(previous, NeuralUnitInput((0.25,), (0.0,)), p)

    assert previous == snapshot
