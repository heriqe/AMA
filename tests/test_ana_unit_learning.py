from dataclasses import replace
import math

import pytest

from ama.ana.unit import NeuralUnitParameters, NeuralUnitState
from ama.ana.unit_learning import (
    UnitLearningPolicy,
    supervised_unit_output_step,
)


def make_parameters(**kwargs):
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=1
    )
    return replace(base, **kwargs)


def make_state(x=0.5, memory=0.2, context=-0.1):
    return NeuralUnitState(
        x=(x,), m=(memory,), c=(context,), g=(1.0,), y=(0.0,)
    )


def test_supervised_step_updates_internal_output_projection_toward_target():
    parameters = make_parameters()
    state = make_state()
    result = supervised_unit_output_step(parameters, state, (0.8,))

    assert result.prediction == (0.0,)
    assert result.error == (0.8,)
    assert result.parameters.w_yx[0][0] > parameters.w_yx[0][0]
    assert result.parameters.w_ym[0][0] > parameters.w_ym[0][0]
    assert result.parameters.w_yc[0][0] < parameters.w_yc[0][0]
    assert result.parameters.b_y[0] > parameters.b_y[0]


def test_repeated_local_updates_reduce_squared_output_error():
    parameters = make_parameters()
    state = make_state()
    target = (0.8,)
    initial = supervised_unit_output_step(parameters, state, target).prediction[0]
    for _ in range(40):
        parameters = supervised_unit_output_step(
            parameters,
            state,
            target,
            UnitLearningPolicy(learning_rate=0.1, max_abs_update=0.05),
        ).parameters
    final = math.tanh(
        parameters.w_yx[0][0] * state.x[0]
        + parameters.w_ym[0][0] * state.m[0]
        + parameters.w_yc[0][0] * state.c[0]
        + parameters.b_y[0]
    )
    assert (target[0] - final) ** 2 < (target[0] - initial) ** 2


def test_only_output_projection_parameters_change():
    parameters = make_parameters(w_xu=((0.25,),), w_yx=((0.1,),))
    result = supervised_unit_output_step(parameters, make_state(), (0.7,))
    updated = result.parameters

    for name in (
        "w_xx", "w_xm", "w_xc", "w_xu", "w_xr", "b_x",
        "w_cc", "w_cx", "w_cr", "b_c",
        "w_gx", "w_gc", "w_gm", "b_g",
        "w_mx", "w_mc", "w_mu", "b_m",
        "rho", "eta", "gamma",
    ):
        assert getattr(updated, name) == getattr(parameters, name)


def test_update_is_bounded_and_deterministic():
    parameters = make_parameters()
    state = make_state()
    policy = UnitLearningPolicy(
        learning_rate=10.0,
        max_abs_weight=0.2,
        max_abs_update=0.01,
    )
    first = supervised_unit_output_step(parameters, state, (1.0,), policy)
    second = supervised_unit_output_step(parameters, state, (1.0,), policy)
    assert first == second
    assert first.max_abs_update_applied <= policy.max_abs_update
    assert all(abs(value) <= policy.max_abs_weight for row in first.parameters.w_yx for value in row)
    assert all(abs(value) <= policy.max_abs_weight for row in first.parameters.w_ym for value in row)
    assert all(abs(value) <= policy.max_abs_weight for row in first.parameters.w_yc for value in row)
    assert all(abs(value) <= policy.max_abs_weight for value in first.parameters.b_y)


def test_inputs_are_not_mutated():
    parameters = make_parameters()
    state = make_state()
    original_parameters, original_state = parameters, state
    supervised_unit_output_step(parameters, state, (0.5,))
    assert parameters == original_parameters
    assert state == original_state


@pytest.mark.parametrize(
    "kwargs",
    [
        {"learning_rate": 0.0},
        {"learning_rate": float("nan")},
        {"max_abs_weight": -1.0},
        {"max_abs_update": float("inf")},
        {"max_abs_feature": 0.0},
        {"max_abs_target": -0.1},
        {"max_abs_update": True},
    ],
)
def test_invalid_learning_policy_is_rejected(kwargs):
    with pytest.raises(ValueError):
        UnitLearningPolicy(**kwargs)


def test_invalid_target_dimension_is_rejected():
    with pytest.raises(ValueError, match="target"):
        supervised_unit_output_step(make_parameters(), make_state(), (0.1, 0.2))


def test_non_finite_target_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        supervised_unit_output_step(make_parameters(), make_state(), (float("nan"),))


def test_target_outside_configured_bound_is_rejected():
    with pytest.raises(ValueError, match="max_abs_target"):
        supervised_unit_output_step(
            make_parameters(),
            make_state(),
            (1.1,),
            UnitLearningPolicy(max_abs_target=1.0),
        )


def test_state_feature_outside_configured_bound_is_rejected():
    with pytest.raises(ValueError, match="max_abs_feature"):
        supervised_unit_output_step(
            make_parameters(),
            make_state(x=11.0),
            (0.5,),
            UnitLearningPolicy(max_abs_feature=10.0),
        )


def test_multi_output_unit_updates_each_output_independently():
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=2
    )
    state = NeuralUnitState(
        x=(0.5,), m=(0.0,), c=(0.0,), g=(1.0,), y=(0.0, 0.0)
    )
    result = supervised_unit_output_step(base, state, (0.7, -0.6))
    assert result.parameters.w_yx[0][0] > 0.0
    assert result.parameters.w_yx[1][0] < 0.0
    assert result.parameters.b_y[0] > 0.0
    assert result.parameters.b_y[1] < 0.0
