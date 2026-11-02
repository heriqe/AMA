import pytest

from ama.ana.temporal_credit import (
    TemporalCreditPolicy,
    fit_recurrent_weight,
    run_temporal_credit_benchmark,
)
from ama.ana.unit import NeuralUnitParameters


def make_parameters():
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=1
    )
    from dataclasses import replace
    return replace(base, w_xu=((0.55,),), w_yx=((1.0,),))


def make_sequence():
    inputs = tuple((index % 7 - 3) / 20 for index in range(60))
    targets = tuple(
        0.55 * value + 0.35 * (inputs[index - 1] if index else 0.0)
        for index, value in enumerate(inputs)
    )
    return inputs, targets


def test_temporal_credit_is_deterministic_and_immutable():
    parameters = make_parameters()
    inputs, targets = make_sequence()
    first = fit_recurrent_weight(parameters, inputs, targets)
    second = fit_recurrent_weight(parameters, inputs, targets)
    assert first == second
    assert parameters.w_xx[0][0] == 0.0


def test_temporal_credit_changes_only_recurrent_coefficient():
    parameters = make_parameters()
    inputs, targets = make_sequence()
    result = fit_recurrent_weight(parameters, inputs, targets)
    assert result.parameters.w_xx[0][0] != parameters.w_xx[0][0]
    assert result.parameters.w_xu == parameters.w_xu
    assert result.parameters.w_yx == parameters.w_yx
    assert result.parameters.w_ym == parameters.w_ym
    assert result.parameters.w_yc == parameters.w_yc
    assert result.parameters.b_x == parameters.b_x
    assert result.parameters.b_y == parameters.b_y


def test_temporal_credit_reduces_sequence_loss_on_controlled_task():
    parameters = make_parameters()
    inputs, targets = make_sequence()
    result = fit_recurrent_weight(
        parameters,
        inputs,
        targets,
        TemporalCreditPolicy(
            learning_rate=0.5,
            finite_difference_epsilon=1e-4,
            max_abs_weight=1.0,
            max_abs_update=0.02,
            max_abs_signal=1.0,
            epochs=100,
        ),
    )
    assert result.final_mse < result.initial_mse


def test_temporal_credit_respects_parameter_and_update_bounds():
    parameters = make_parameters()
    inputs, targets = make_sequence()
    result = fit_recurrent_weight(
        parameters,
        inputs,
        targets,
        TemporalCreditPolicy(max_abs_weight=0.1, max_abs_update=0.001),
    )
    assert abs(result.final_recurrent_weight) <= 0.1
    assert abs(result.final_recurrent_weight) <= 0.1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"learning_rate": 0.0},
        {"finite_difference_epsilon": float("nan")},
        {"max_abs_weight": -1.0},
        {"max_abs_update": float("inf")},
        {"max_abs_signal": True},
        {"epochs": 0},
        {"epochs": 2001},
        {"epochs": True},
    ],
)
def test_temporal_credit_policy_rejects_invalid_values(kwargs):
    with pytest.raises(ValueError):
        TemporalCreditPolicy(**kwargs)


@pytest.mark.parametrize("seed", [True, "41", 1.2])
def test_benchmark_rejects_invalid_seed(seed):
    with pytest.raises(ValueError, match="seed"):
        run_temporal_credit_benchmark(seed=seed)


@pytest.mark.parametrize("value", [0, 19, 5001, True, 2.5])
def test_benchmark_rejects_invalid_phase_lengths(value):
    with pytest.raises(ValueError):
        run_temporal_credit_benchmark(train_steps=value)


def test_temporal_credit_benchmark_is_deterministic():
    assert run_temporal_credit_benchmark() == run_temporal_credit_benchmark()


def test_temporal_credit_benchmark_learns_a_recurrent_contribution():
    report = run_temporal_credit_benchmark()
    assert report.final_train_mse < report.initial_train_mse
    assert report.learned_recurrent_weight > report.initial_recurrent_weight
    assert report.learned_mse < report.fixed_mse
