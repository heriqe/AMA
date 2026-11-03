import math
from dataclasses import replace

import pytest

from ama.ana.multivariate_temporal_gradient import (
    compare_multivariate_temporal_gradients,
)
from ama.ana.unit import NeuralUnitParameters


def make_parameters():
    base = NeuralUnitParameters.zeros(
        input_size=1,
        relation_size=1,
        internal_size=1,
        output_size=1,
        rho=0.8,
        eta=0.0,
        gamma=0.0,
    )
    return replace(base, w_xu=((0.55,),), w_yx=((1.0,),))


def test_two_analytic_temporal_gradients_match_central_differences():
    parameters = make_parameters()
    inputs = tuple(((index * 7) % 19 - 9) / 30 for index in range(80))
    targets = tuple(
        0.55 * value + 0.35 * (inputs[index - 1] if index else 0.0)
        for index, value in enumerate(inputs)
    )
    report = compare_multivariate_temporal_gradients(parameters, inputs, targets)

    assert len(report.comparisons) == 24
    assert report.analytic_sequence_evaluations == 4
    assert report.finite_difference_sequence_evaluations == 48
    assert report.scenario_count == 4
    assert report.parameter_count == 2
    assert report.sequence_steps == 80
    assert {item.parameter_name for item in report.comparisons} == {
        "w_xx[0][0]",
        "w_xu[0][0]",
    }
    for comparison in report.comparisons:
        assert math.isfinite(comparison.analytic_gradient)
        assert math.isfinite(comparison.finite_difference_gradient)
        assert comparison.absolute_error < 1e-7


def test_both_parameter_gradients_are_independently_nonzero_in_reference_case():
    parameters = make_parameters()
    inputs = (0.2, -0.1, 0.3, 0.15, -0.25)
    targets = (0.1, -0.05, 0.2, 0.08, -0.1)
    report = compare_multivariate_temporal_gradients(
        parameters,
        inputs,
        targets,
        scenarios=((0.25, 0.4),),
        epsilons=(1e-4,),
    )
    gradients = {item.parameter_name: item.analytic_gradient
                 for item in report.comparisons}
    assert abs(gradients["w_xx[0][0]"]) > 1e-8
    assert abs(gradients["w_xu[0][0]"]) > 1e-8


@pytest.mark.parametrize(
    "scenarios,epsilons",
    [
        ((), (1e-4,)),
        (((0.1,),), (1e-4,)),
        (((0.1, 0.2),), (0.0,)),
        (((float("nan"), 0.2),), (1e-4,)),
        (((0.1, 0.2),), (float("inf"),)),
    ],
)
def test_multivariate_gradient_validation_rejects_invalid_inputs(scenarios, epsilons):
    parameters = make_parameters()
    with pytest.raises(ValueError):
        compare_multivariate_temporal_gradients(
            parameters, (0.1, 0.2), (0.0, 0.1),
            scenarios=scenarios, epsilons=epsilons,
        )


def test_multivariate_gradient_validation_rejects_mismatched_sequences():
    with pytest.raises(ValueError):
        compare_multivariate_temporal_gradients(
            make_parameters(), (0.1, 0.2), (0.0,)
        )
