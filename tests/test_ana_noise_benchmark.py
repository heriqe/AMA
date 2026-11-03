import pytest

from ama.ana.benchmark import run_noise_robustness_benchmark


def test_noise_benchmark_is_reproducible_for_same_seeds():
    first = run_noise_robustness_benchmark(seeds=(3, 11), steps_per_phase=8)
    second = run_noise_robustness_benchmark(seeds=(3, 11), steps_per_phase=8)
    assert first == second


def test_noise_benchmark_uses_same_three_variants():
    report = run_noise_robustness_benchmark(seeds=(5,), steps_per_phase=5)
    assert tuple(item.name for item in report.variants) == (
        "fixed",
        "weight_only",
        "structural",
    )
    assert report.seeds == (5,)
    assert report.noise_amplitude == 0.1


def test_noise_benchmark_reports_non_negative_finite_metrics():
    report = run_noise_robustness_benchmark(seeds=(1, 2, 3), steps_per_phase=10)
    for variant in report.variants:
        assert variant.mean_tracking_error >= 0.0
        assert variant.tracking_error_stddev >= 0.0
        assert 0.0 <= variant.mean_active_step_fraction <= 1.0
        assert variant.mean_activations >= 0.0
        assert variant.mean_deactivations >= 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"seeds": ()},
        {"seeds": (1, 1)},
        {"seeds": (True,)},
        {"seeds": (1.5,)},
        {"seeds": list((1, 2))},
        {"seeds": tuple(range(101))},
        {"steps_per_phase": 0},
        {"steps_per_phase": True},
        {"noise_amplitude": -0.01},
        {"noise_amplitude": 0.51},
        {"noise_amplitude": float("nan")},
        {"noise_amplitude": True},
    ],
)
def test_noise_benchmark_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        run_noise_robustness_benchmark(**kwargs)
