import pytest

from ama.ana.benchmark import run_plasticity_benchmark


def test_benchmark_is_deterministic():
    assert run_plasticity_benchmark() == run_plasticity_benchmark()


def test_benchmark_compares_three_variants():
    report = run_plasticity_benchmark(steps_per_phase=8)
    assert tuple(item.name for item in report.variants) == (
        "fixed",
        "weight_only",
        "structural",
    )
    assert report.targets == (1.0, -1.0, 0.0, 1.0)


def test_structural_variant_exercises_topology_changes():
    report = run_plasticity_benchmark()
    structural = report.variants[2]
    assert structural.activations >= 2
    assert structural.deactivations >= 1
    assert 0.0 <= structural.active_step_fraction <= 1.0
    assert abs(structural.final_weight) <= 1.0


def test_weight_only_variant_never_changes_topology():
    report = run_plasticity_benchmark()
    weight_only = report.variants[1]
    assert weight_only.activations == 0
    assert weight_only.deactivations == 0
    assert weight_only.final_active


@pytest.mark.parametrize("steps", [0, -1, 10001, True, 1.5])
def test_invalid_benchmark_step_count_is_rejected(steps):
    with pytest.raises(ValueError, match="steps_per_phase"):
        run_plasticity_benchmark(steps)
