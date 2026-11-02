import pytest

from ama.ana.forecast import run_forecast_benchmark


def test_forecast_benchmark_is_deterministic():
    assert run_forecast_benchmark() == run_forecast_benchmark()


def test_forecast_benchmark_uses_three_network_variants_and_held_out_steps():
    report = run_forecast_benchmark(train_steps=40, evaluation_steps=25)
    assert tuple(item.name for item in report.variants) == (
        "fixed",
        "weight_only",
        "structural",
    )
    assert report.train_steps == 40
    assert report.evaluation_steps == 25
    assert report.persistence_baseline_mse >= 0.0
    for item in report.variants:
        assert item.mean_squared_error >= 0.0
        assert item.mean_absolute_error >= 0.0
        assert abs(item.final_edge_weight) <= 0.8
        assert isinstance(item.final_edge_active, bool)


def test_forecast_benchmark_reports_a_separate_persistence_baseline():
    report = run_forecast_benchmark(seed=9, train_steps=30, evaluation_steps=20)
    assert report.persistence_baseline_mse > 0.0


@pytest.mark.parametrize("steps", [0, 19, 10001, True, 1.5])
def test_invalid_training_steps_are_rejected(steps):
    with pytest.raises(ValueError, match="train_steps"):
        run_forecast_benchmark(train_steps=steps)


@pytest.mark.parametrize("steps", [0, 19, 10001, True, 1.5])
def test_invalid_evaluation_steps_are_rejected(steps):
    with pytest.raises(ValueError, match="evaluation_steps"):
        run_forecast_benchmark(evaluation_steps=steps)


@pytest.mark.parametrize("seed", [True, 1.5, "23"])
def test_invalid_seed_is_rejected(seed):
    with pytest.raises(ValueError, match="seed"):
        run_forecast_benchmark(seed=seed)
