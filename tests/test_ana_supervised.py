import pytest

from ama.ana.supervised import (
    LinearReadoutParameters,
    predict_readout,
    train_readout_step,
)


def test_supervised_step_reduces_error_on_linear_sample():
    model = LinearReadoutParameters(weights=((0.0,),), bias=(0.0,), learning_rate=0.1)
    before = predict_readout(model, (1.0,))
    trained = train_readout_step(model, (1.0,), (1.0,))
    after = predict_readout(trained, (1.0,))
    assert abs(after[0] - 1.0) < abs(before[0] - 1.0)
    assert model.weights == ((0.0,),)


def test_supervised_dimensions_and_non_finite_values_are_rejected():
    model = LinearReadoutParameters(weights=((0.0,),), bias=(0.0,), learning_rate=0.1)
    with pytest.raises(ValueError, match="length"):
        predict_readout(model, (1.0, 2.0))
    with pytest.raises(ValueError, match="finite"):
        train_readout_step(model, (float("inf"),), (1.0,))
    with pytest.raises(ValueError, match="positive"):
        LinearReadoutParameters(weights=((0.0,),), bias=(0.0,), learning_rate=0.0)


def test_supervised_parameter_limit_rejects_update_without_clipping():
    model = LinearReadoutParameters(
        weights=((0.9,),), bias=(0.0,), learning_rate=1.0, max_abs_parameter=1.0
    )
    with pytest.raises(ValueError, match="exceeds configured limit"):
        train_readout_step(model, (1.0,), (-1.0,))



def test_supervised_training_beats_constant_mean_baseline():
    model = LinearReadoutParameters(
        weights=((0.0,),), bias=(0.0,), learning_rate=0.05
    )
    samples = [(-1.0, -1.0), (0.0, 1.0), (1.0, 3.0)]
    mean_target = sum(target for _, target in samples) / len(samples)
    baseline_mse = sum((mean_target - target) ** 2 for _, target in samples) / len(samples)

    trained = model
    for _ in range(120):
        for feature, target in samples:
            trained = train_readout_step(trained, (feature,), (target,))

    learned_mse = sum(
        (predict_readout(trained, (feature,))[0] - target) ** 2
        for feature, target in samples
    ) / len(samples)
    assert learned_mse < baseline_mse
