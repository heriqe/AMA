"""Synchronous directed graph execution for ANA v0.2."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

from ama.ana.unit import (
    NeuralUnitInput,
    NeuralUnitParameters,
    NeuralUnitState,
    Vector,
    _as_vector,
    step as step_unit,
)


MAX_NETWORK_UNITS = 10_000
MAX_NETWORK_CONNECTIONS = 100_000


@dataclass(frozen=True, slots=True)
class NetworkNode:
    """A uniquely identified unit and its fixed local parameters."""

    node_id: str
    parameters: NeuralUnitParameters

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id.strip():
            raise ValueError("node_id must be a non-empty string")


@dataclass(frozen=True, slots=True)
class Connection:
    """A directed scalar-weighted connection from source to target."""

    source: str
    target: str
    weight: float

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("connection source must be a non-empty string")
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("connection target must be a non-empty string")
        if isinstance(self.weight, bool) or not isinstance(self.weight, (int, float)):
            raise ValueError("connection weight must be numeric")
        if not math.isfinite(self.weight):
            raise ValueError("connection weight must be finite")


@dataclass(frozen=True, slots=True)
class NetworkDefinition:
    """Immutable topology and local parameters for a synchronous ANA graph."""

    nodes: tuple[NetworkNode, ...]
    connections: tuple[Connection, ...]

    def __post_init__(self) -> None:
        if not self.nodes:
            raise ValueError("network must contain at least one node")
        if len(self.nodes) > MAX_NETWORK_UNITS:
            raise ValueError(f"network exceeds {MAX_NETWORK_UNITS} nodes")
        if len(self.connections) > MAX_NETWORK_CONNECTIONS:
            raise ValueError(
                f"network exceeds {MAX_NETWORK_CONNECTIONS} connections"
            )

        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node IDs must be unique")

        relation_sizes = {node.parameters.relation_size for node in self.nodes}
        if len(relation_sizes) != 1:
            raise ValueError("all nodes must share the same relation_size")
        relation_size = next(iter(relation_sizes))
        if any(node.parameters.output_size != relation_size for node in self.nodes):
            raise ValueError(
                "each node output_size must equal the network relation_size"
            )

        known_ids = set(node_ids)
        seen_edges: set[tuple[str, str]] = set()
        for edge in self.connections:
            if edge.source not in known_ids or edge.target not in known_ids:
                raise ValueError("connection references an unknown node")
            pair = (edge.source, edge.target)
            if pair in seen_edges:
                raise ValueError("parallel connections are not supported")
            seen_edges.add(pair)


@dataclass(frozen=True, slots=True)
class NodeState:
    """State of one node in a network snapshot."""

    node_id: str
    state: NeuralUnitState


@dataclass(frozen=True, slots=True)
class NetworkState:
    """Immutable snapshot of all node states at one discrete time step."""

    nodes: tuple[NodeState, ...]

    @classmethod
    def initial(cls, network: NetworkDefinition) -> "NetworkState":
        """Create initial local states for every node in definition order."""
        return cls(
            nodes=tuple(
                NodeState(node.node_id, NeuralUnitState.initial(node.parameters))
                for node in network.nodes
            )
        )


def step_network(
    network: NetworkDefinition,
    state: NetworkState,
    external_inputs: Mapping[str, Vector],
) -> NetworkState:
    """Advance all nodes synchronously using only outputs from the old snapshot."""
    node_by_id = {node.node_id: node for node in network.nodes}
    state_by_id: dict[str, NeuralUnitState] = {}
    for item in state.nodes:
        if item.node_id in state_by_id:
            raise ValueError("network state contains duplicate node IDs")
        state_by_id[item.node_id] = item.state

    if set(state_by_id) != set(node_by_id):
        raise ValueError("network state node IDs must match network definition")
    if set(external_inputs) != set(node_by_id):
        raise ValueError("external inputs must be provided for every network node")

    old_outputs = {
        node_id: _as_vector(
            local_state.y,
            f"state[{node_id}].y",
            node_by_id[node_id].parameters.output_size,
        )
        for node_id, local_state in state_by_id.items()
    }

    incoming: dict[str, list[tuple[str, float]]] = {
        node_id: [] for node_id in node_by_id
    }
    for edge in network.connections:
        incoming[edge.target].append((edge.source, float(edge.weight)))

    next_states: list[NodeState] = []
    for node in network.nodes:
        relation_size = node.parameters.relation_size
        relational = [0.0] * relation_size
        for source_id, weight in sorted(incoming[node.node_id]):
            source_output = old_outputs[source_id]
            for index, value in enumerate(source_output):
                relational[index] += weight * value

        local_input = NeuralUnitInput(
            external=_as_vector(
                external_inputs[node.node_id],
                f"external_inputs[{node.node_id}]",
                node.parameters.input_size,
            ),
            relational=tuple(relational),
        )
        next_state = step_unit(
            state_by_id[node.node_id],
            local_input,
            node.parameters,
        )
        next_states.append(NodeState(node.node_id, next_state))

    return NetworkState(nodes=tuple(next_states))
