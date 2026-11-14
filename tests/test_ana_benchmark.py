import pytest

from ama.ana.benchmark import (
    run_noisy_plasticity_benchmark,
    run_plasticity_benchmark,
)


def test_benchmark_is_deterministic():
    assert run_plasticity_benchmark() == run_plasticity_benchmark()


def test_benchmark_compares_fixed_weight_only_and_structural_variants():
    report = run_plasticity_benchmark(steps_per_phase=8)
    assert report.targets == (1.0, -1.0, 0.0, 1.0)
    assert tuple(item.name for item in report.variants) == (
        "fixed",
        "weight_only",
        "structural",
    )


def test_structural_variant_exercises_activation_and_pruning():
    report = run_plasticity_benchmark()
    structural = report.variants[2]
    assert structural.activations == 2
    assert structural.deactivations == 1
    assert structural.active_step_fraction == pytest.approx(0.88125)
    assert structural.max_abs_weight_observed <= 1.0


def test_weight_only_baseline_tracks_target_better_in_reference_protocol():
    report = run_plasticity_benchmark()
    weight_only = report.variants[1]
    structural = report.variants[2]
    assert weight_only.mean_absolute_tracking_error == pytest.approx(0.1323, abs=1e-4)
    assert structural.mean_absolute_tracking_error == pytest.approx(0.1643, abs=1e-4)
    assert weight_only.mean_absolute_tracking_error < structural.mean_absolute_tracking_error


@pytest.mark.parametrize("steps", [0, -1, 10_001, True, 1.5])
def test_invalid_benchmark_step_count_is_rejected(steps):
    with pytest.raises(ValueError, match="steps_per_phase"):
        run_plasticity_benchmark(steps)


def test_noisy_benchmark_is_deterministic_and_reports_seed_dispersion():
    first = run_noisy_plasticity_benchmark(noise_amplitude=0.1, seeds=(1, 2, 3, 4, 5))
    second = run_noisy_plasticity_benchmark(noise_amplitude=0.1, seeds=(1, 2, 3, 4, 5))
    assert first == second
    assert first.seeds == (1, 2, 3, 4, 5)
    assert tuple(item.name for item in first.variants) == ("fixed", "weight_only", "structural")
    assert all(item.between_seed_error_stddev >= 0.0 for item in first.variants)
    assert all(item.max_abs_weight_observed <= 1.0 for item in first.variants)
    assert any(item.between_seed_error_stddev > 0.0 for item in first.variants)


def test_zero_noise_matches_reference_benchmark():
    reference = run_plasticity_benchmark()
    robust = run_noisy_plasticity_benchmark(noise_amplitude=0.0, seeds=(11, 12, 13))
    for expected, observed in zip(reference.variants, robust.variants):
        assert observed.mean_absolute_tracking_error == pytest.approx(
            expected.mean_absolute_tracking_error
        )
        assert observed.mean_active_step_fraction == pytest.approx(
            expected.active_step_fraction
        )
        assert observed.between_seed_error_stddev == pytest.approx(0.0)


@pytest.mark.parametrize("noise", [-0.1, 1.1, float("nan"), float("inf"), True, "0.1"])
def test_invalid_noise_amplitude_is_rejected(noise):
    with pytest.raises(ValueError, match="noise_amplitude"):
        run_noisy_plasticity_benchmark(noise_amplitude=noise)


@pytest.mark.parametrize(
    "seeds",
    [(), (1, 1), (-1,), (True,), (1.5,), None],
)
def test_invalid_seed_collections_are_rejected(seeds):
    with pytest.raises(ValueError, match="seeds"):
        run_noisy_plasticity_benchmark(seeds=seeds)


def test_robustness_benchmark_rejects_excessive_workload():
    with pytest.raises(ValueError, match="100000"):
        run_noisy_plasticity_benchmark(steps_per_phase=10_000, seeds=range(3))
