"""Topology graph construction."""

import networkx as nx

from .models import TopologySpec


def build_topology_graph(topology: TopologySpec) -> nx.DiGraph:
    """Build a directed graph whose edges point from caller to dependency."""
    graph = nx.DiGraph()
    graph.add_nodes_from(service.name for service in topology.services)
    graph.add_edges_from((edge.from_service, edge.to_service) for edge in topology.depends_on)
    return graph
