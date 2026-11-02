import math

import pytest

from ama.ana.temporal_gradient_validation import compare_temporal_gradients
from ama.ana.unit import NeuralUnitParameters


def make_parameters():
    return NeuralUnitParameters.zeros(
        input_size=1,
        relation_size=1,
        internal_size=1,
        output_size=1,
        rho=0.8,
        eta=0.0,
        gamma=0.0,
    ).__class__(
        **{
            **{
                field: getattr(NeuralUnitParameters.zeros(
                    input_size=1, relation_size=1, internal_size=1, output_size=1,
                    rho=0.8, eta=0.0, gamma=0.0,
                ), field)
                for field in NeuralUnitParameters.__dataclass_fields__
            },
            "w_xu": ((0.55,),),
            "w_yx": ((1.0,),),
        }
    )


def test_analytic_temporal_gradient_matches_central_difference_across_epsilons():
    parameters = make_parameters()
    inputs = tuple(((index * 7) % 19 - 9) / 30 for index in range(80))
    targets = tuple(
        0.55 * value + 0.35 * (inputs[index - 1] if index else 0.0)
        for index, value in enumerate(inputs)
    )
    report = compare_temporal_gradients(parameters, inputs, targets)
    assert len(report.comparisons) == 20
    assert report.analytic_sequence_evaluations == 4
    assert report.finite_difference_sequence_evaluations == 40
    assert report.sequence_steps == 80
    for comparison in report.comparisons:
        assert math.isfinite(comparison.analytic_gradient)
        assert math.isfinite(comparison.finite_difference_gradient)
        assert comparison.absolute_error < 1e-6


def test_central_difference_error_decreases_for_reasonable_epsilon_range():
    parameters = make_parameters()
    inputs = tuple((index % 11 - 5) / 20 for index in range(50))
    targets = tuple(0.2 * value + 0.1 * (inputs[index - 1] if index else 0.0)
                    for index, value in enumerate(inputs))
    report = compare_temporal_gradients(
        parameters, inputs, targets,
        recurrent_weights=(0.25,), epsilons=(1e-2, 1e-3, 1e-4),
    )
    errors = [item.absolute_error for item in report.comparisons]
    assert errors[1] < errors[0]
    assert errors[2] < errors[1]


@pytest.mark.parametrize("epsilons", [(), (0.0,), (-1e-4,), (float("nan"),)])
def test_gradient_validation_rejects_invalid_epsilons(epsilons):
    parameters = make_parameters()
    with pytest.raises(ValueError):
        compare_temporal_gradients(parameters, (0.1, 0.2), (0.0, 0.1),
                                   epsilons=epsilons)


def test_gradient_validation_rejects_non_reference_state_pathways():
    from dataclasses import replace

    parameters = replace(make_parameters(), w_xm=((0.1,),))
    with pytest.raises(ValueError, match="pathways"):
        compare_temporal_gradients(parameters, (0.1, 0.2), (0.0, 0.1))


def test_gradient_validation_rejects_invalid_sequence():
    parameters = make_parameters()
    with pytest.raises(ValueError):
        compare_temporal_gradients(parameters, (0.1,), (0.0,))
