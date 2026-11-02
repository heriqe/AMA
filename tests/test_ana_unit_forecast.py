import pytest

from ama.ana.unit_forecast import (
    run_unit_forecast_benchmark,
    run_unit_forecast_suite,
)


def test_unit_forecast_benchmark_is_deterministic():
    assert run_unit_forecast_benchmark() == run_unit_forecast_benchmark()


def test_unit_forecast_uses_held_out_future_segment():
    report = run_unit_forecast_benchmark(
        seed=13, train_steps=50, evaluation_steps=30
    )
    assert report.train_steps == 50
    assert report.evaluation_steps == 30
    assert report.fixed_mse >= 0.0
    assert report.fixed_mae >= 0.0
    assert report.learned_mse >= 0.0
    assert report.learned_mae >= 0.0
    assert report.persistence_mse >= 0.0
    assert abs(report.final_output_weight) <= 2.0
    assert abs(report.final_output_bias) <= 2.0


def test_learned_unit_output_improves_over_zero_projection_on_default_task():
    report = run_unit_forecast_benchmark()
    assert report.learned_mse < report.fixed_mse


@pytest.mark.parametrize("seed", [True, 1.5, "41"])
def test_unit_forecast_rejects_invalid_seed(seed):
    with pytest.raises(ValueError, match="seed"):
        run_unit_forecast_benchmark(seed=seed)


@pytest.mark.parametrize("name", ["train_steps", "evaluation_steps"])
@pytest.mark.parametrize("value", [0, 19, 10001, True, 1.5])
def test_unit_forecast_rejects_invalid_phase_lengths(name, value):
    with pytest.raises(ValueError, match=name):
        run_unit_forecast_benchmark(**{name: value})


def test_unit_forecast_suite_is_reproducible_and_paired():
    seeds = (2, 5, 11)
    report = run_unit_forecast_suite(
        seeds, train_steps=50, evaluation_steps=30
    )
    assert report == run_unit_forecast_suite(
        seeds, train_steps=50, evaluation_steps=30
    )
    assert report.seeds == seeds
    assert tuple(item.seed for item in report.reports) == seeds
    assert tuple(item.name for item in report.aggregates) == ("fixed", "learned")


def test_unit_forecast_suite_aggregates_metrics_correctly():
    report = run_unit_forecast_suite(
        (2, 5, 11), train_steps=50, evaluation_steps=30
    )
    for aggregate, field in zip(
        report.aggregates, ("fixed_mse", "learned_mse")
    ):
        values = tuple(getattr(item, field) for item in report.reports)
        assert aggregate.mean_mse == pytest.approx(sum(values) / len(values))
        assert aggregate.std_mse >= 0.0


@pytest.mark.parametrize(
    "seeds",
    [(), [], (1, 1), (True, 2), (1, 2.5), "1,2"],
)
def test_unit_forecast_suite_rejects_invalid_seed_collections(seeds):
    with pytest.raises(ValueError, match="seeds"):
        run_unit_forecast_suite(
            seeds, train_steps=20, evaluation_steps=20
        )
