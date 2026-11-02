from dataclasses import replace
import math

import pytest

from ama.ana.network import (
    Connection,
    NetworkDefinition,
    NetworkNode,
    NetworkState,
    NodeState,
    step_network,
)
from ama.ana.unit import NeuralUnitInput, NeuralUnitParameters, NeuralUnitState, step


def params(**kwargs):
    base = NeuralUnitParameters.zeros(
        input_size=1, relation_size=1, internal_size=1, output_size=1
    )
    return replace(base, **kwargs)


def network(*, nodes, connections=()):
    return NetworkDefinition(tuple(nodes), tuple(connections))


def inputs(*node_ids):
    return {node_id: (0.0,) for node_id in node_ids}


def test_single_node_network_matches_isolated_unit():
    p = params(w_xu=((0.8,),), w_yx=((1.0,),))
    graph = network(nodes=[NetworkNode("a", p)])
    old_state = NetworkState.initial(graph)
    external = {"a": (0.5,)}

    graph_result = step_network(graph, old_state, external)
    unit_result = step(
        old_state.nodes[0].state,
        NeuralUnitInput(external["a"], (0.0,)),
        p,
    )

    assert graph_result.nodes[0].state == unit_result


def test_connection_uses_previous_source_output():
    source = params(w_xu=((1.0,),), w_yx=((1.0,),))
    target = params(w_xr=((1.0,),), w_yx=((1.0,),))
    graph = network(
        nodes=[NetworkNode("source", source), NetworkNode("target", target)],
        connections=[Connection("source", "target", 0.5)],
    )
    old_state = NetworkState.initial(graph)

    first = step_network(
        graph, old_state, {"source": (1.0,), "target": (0.0,)}
    )
    assert first.nodes[1].state.x == (0.0,)

    second = step_network(
        graph, first, {"source": (0.0,), "target": (0.0,)}
    )
    expected_source_y = first.nodes[0].state.y[0]
    assert second.nodes[1].state.x[0] == pytest.approx(
        math.tanh(0.5 * expected_source_y)
    )


def test_multiple_incoming_signals_are_summed():
    source = params(w_xu=((1.0,),), w_yx=((1.0,),))
    target = params(w_xr=((1.0,),))
    graph = network(
        nodes=[
            NetworkNode("a", source),
            NetworkNode("b", source),
            NetworkNode("target", target),
        ],
        connections=[
            Connection("a", "target", 0.5),
            Connection("b", "target", 0.25),
        ],
    )
    first = step_network(
        graph,
        NetworkState.initial(graph),
        {"a": (1.0,), "b": (0.5,), "target": (0.0,)},
    )
    second = step_network(graph, first, inputs("a", "b", "target"))
    received = 0.5 * first.nodes[0].state.y[0] + 0.25 * first.nodes[1].state.y[0]

    assert second.nodes[2].state.x[0] == pytest.approx(math.tanh(received))


def test_recurrent_cycle_is_synchronous_and_order_independent():
    p = params(w_xr=((1.0,),), w_yx=((1.0,),))
    forward = network(
        nodes=[NetworkNode("a", p), NetworkNode("b", p)],
        connections=[Connection("a", "b", 1.0), Connection("b", "a", 1.0)],
    )
    reversed_order = network(
        nodes=[NetworkNode("b", p), NetworkNode("a", p)],
        connections=[Connection("b", "a", 1.0), Connection("a", "b", 1.0)],
    )
    initial_a = NetworkState.initial(forward)
    initial_b = NetworkState.initial(reversed_order)
    state_a = NetworkState(
        nodes=(
            NodeState("a", NeuralUnitState((0.0,), (0.0,), (0.0,), (1.0,), (0.7,))),
            NodeState("b", NeuralUnitState((0.0,), (0.0,), (0.0,), (1.0,), (-0.2,))),
        )
    )
    state_b = NetworkState(
        nodes=(
            NodeState("b", state_a.nodes[1].state),
            NodeState("a", state_a.nodes[0].state),
        )
    )
    result_a = step_network(forward, state_a, inputs("a", "b"))
    result_b = step_network(reversed_order, state_b, inputs("a", "b"))

    by_id_a = {item.node_id: item.state for item in result_a.nodes}
    by_id_b = {item.node_id: item.state for item in result_b.nodes}
    assert by_id_a == by_id_b


def test_unconnected_node_receives_zero_relational_signal():
    p = params(w_xr=((1.0,),))
    graph = network(nodes=[NetworkNode("isolated", p)])
    result = step_network(graph, NetworkState.initial(graph), inputs("isolated"))

    assert result.nodes[0].state.x == (0.0,)


def test_duplicate_node_ids_are_rejected():
    p = params()
    with pytest.raises(ValueError, match="unique"):
        network(nodes=[NetworkNode("x", p), NetworkNode("x", p)])


def test_unknown_connection_endpoint_is_rejected():
    p = params()
    with pytest.raises(ValueError, match="unknown node"):
        network(
            nodes=[NetworkNode("a", p)],
            connections=[Connection("a", "missing", 1.0)],
        )


def test_incompatible_relation_dimensions_are_rejected():
    p1 = params()
    p2 = NeuralUnitParameters.zeros(
        input_size=1, relation_size=2, internal_size=1, output_size=2
    )
    with pytest.raises(ValueError, match="share the same relation_size"):
        network(nodes=[NetworkNode("a", p1), NetworkNode("b", p2)])


def test_non_finite_connection_weight_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        Connection("a", "b", float("inf"))


def test_external_inputs_must_match_node_set():
    p = params()
    graph = network(nodes=[NetworkNode("a", p)])
    with pytest.raises(ValueError, match="every network node"):
        step_network(graph, NetworkState.initial(graph), {})


def test_network_step_does_not_mutate_previous_snapshot():
    p = params(w_xu=((1.0,),))
    graph = network(nodes=[NetworkNode("a", p)])
    old_state = NetworkState.initial(graph)

    step_network(graph, old_state, {"a": (0.25,)})

    assert old_state == NetworkState.initial(graph)
