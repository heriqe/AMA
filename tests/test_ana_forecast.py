import pytest

from ama.ana.forecast import run_forecast_benchmark, run_forecast_suite


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


def test_forecast_suite_is_reproducible_and_preserves_paired_runs():
    seeds = (3, 7, 11)
    report = run_forecast_suite(seeds, train_steps=40, evaluation_steps=25)
    assert report == run_forecast_suite(seeds, train_steps=40, evaluation_steps=25)
    assert report.seeds == seeds
    assert tuple(item.seed for item in report.reports) == seeds
    assert tuple(item.name for item in report.aggregates) == (
        "fixed",
        "weight_only",
        "structural",
    )
    assert all(item.std_mse >= 0.0 and item.std_mae >= 0.0 for item in report.aggregates)


def test_forecast_suite_uses_population_mean_and_standard_deviation():
    report = run_forecast_suite((3, 7, 11), train_steps=40, evaluation_steps=25)
    for aggregate in report.aggregates:
        values = tuple(
            next(v for v in run.variants if v.name == aggregate.name).mean_squared_error
            for run in report.reports
        )
        expected_mean = sum(values) / len(values)
        expected_std = (
            sum((value - expected_mean) ** 2 for value in values) / len(values)
        ) ** 0.5
        assert aggregate.mean_mse == pytest.approx(expected_mean)
        assert aggregate.std_mse == pytest.approx(expected_std)


@pytest.mark.parametrize(
    "seeds",
    [(), [], (1, 1), (True, 2), (1, 2.5), "1,2"],
)
def test_forecast_suite_rejects_invalid_seed_collections(seeds):
    with pytest.raises(ValueError, match="seeds"):
        run_forecast_suite(seeds)


def test_forecast_suite_reports_baseline_aggregate():
    report = run_forecast_suite((3, 7, 11), train_steps=40, evaluation_steps=25)
    values = tuple(item.persistence_baseline_mse for item in report.reports)
    assert report.mean_persistence_mse == pytest.approx(sum(values) / len(values))
    assert report.std_persistence_mse >= 0.0
