import pytest

from ama.ana.temporal_credit import run_temporal_credit_suite


def test_temporal_credit_suite_is_deterministic_and_paired():
    seeds = (2, 5, 11)
    first = run_temporal_credit_suite(
        seeds, train_steps=40, evaluation_steps=25
    )
    second = run_temporal_credit_suite(
        seeds, train_steps=40, evaluation_steps=25
    )
    assert first == second
    assert first.seeds == seeds
    assert tuple(report.seed for report in first.reports) == seeds
    assert tuple(item.name for item in first.aggregates) == ("fixed", "learned")


def test_temporal_credit_suite_aggregates_metrics():
    report = run_temporal_credit_suite(
        (2, 5, 11), train_steps=40, evaluation_steps=25
    )
    for aggregate, mse_name, mae_name in (
        (report.aggregates[0], "fixed_mse", "fixed_mae"),
        (report.aggregates[1], "learned_mse", "learned_mae"),
    ):
        mse = tuple(getattr(item, mse_name) for item in report.reports)
        mae = tuple(getattr(item, mae_name) for item in report.reports)
        assert aggregate.mean_mse == pytest.approx(sum(mse) / len(mse))
        assert aggregate.mean_mae == pytest.approx(sum(mae) / len(mae))
        assert aggregate.std_mse >= 0.0
        assert aggregate.std_mae >= 0.0


@pytest.mark.parametrize(
    "seeds",
    [(), [], (1, 1), (True, 2), (1, 2.5), "1,2"],
)
def test_temporal_credit_suite_rejects_invalid_seed_sets(seeds):
    with pytest.raises(ValueError, match="seeds"):
        run_temporal_credit_suite(
            seeds, train_steps=20, evaluation_steps=20
        )


def test_reference_multi_seed_suite_improves_held_out_forecast():
    report = run_temporal_credit_suite()
    fixed = report.aggregates[0]
    learned = report.aggregates[1]
    assert learned.mean_mse < fixed.mean_mse
    assert learned.mean_mae < fixed.mean_mae
