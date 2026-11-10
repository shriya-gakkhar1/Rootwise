from pathlib import Path

from rootwise_sim.graph import build_topology_graph
from rootwise_sim.loader import load_scenario, load_topology

SCENARIOS = Path(__file__).parents[2] / "scenarios"


def test_specs_load_and_validate() -> None:
    topology = load_topology(SCENARIOS / "topology.yaml")
    scenario = load_scenario(SCENARIOS / "s1_pool_exhaustion.yaml")
    assert len(topology.services) == 8
    assert scenario.ground_truth.cause_node == "postgres"


def test_topology_reachability() -> None:
    graph = build_topology_graph(load_topology(SCENARIOS / "topology.yaml"))
    assert nx_has_path(graph, "frontend", "postgres")


def nx_has_path(graph, source: str, target: str) -> bool:
    """Keep the test assertion readable while avoiding an extra public API."""
    import networkx as nx

    return nx.has_path(graph, source, target)
