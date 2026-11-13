import pytest

from ama.ana.benchmark import run_plasticity_benchmark


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
