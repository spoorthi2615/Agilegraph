from typing import Dict, List, Optional
from uuid import UUID

from app.models.graph_edge import GraphEdge
from app.models.graph_node import GraphNode


class CryptoGraph:
    """
    In-memory representation of the cryptographic dependency graph.
    This class manages nodes and edges purely locally, independent of any external database.
    """

    def __init__(self) -> None:
        self.nodes: Dict[UUID, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        """
        Registers a node into the graph.

        Raises:
            ValueError: If a node with the identical node_id already exists.
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node with ID {node.node_id} already exists in the graph.")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """
        Registers a directional edge into the graph.

        Raises:
            ValueError: If either the source or target nodes do not exist in the graph.
        """
        if edge.source_node not in self.nodes:
            raise ValueError(f"Source node {edge.source_node} does not exist in the graph.")
        if edge.target_node not in self.nodes:
            raise ValueError(f"Target node {edge.target_node} does not exist in the graph.")

        self.edges.append(edge)

    def get_node(self, node_id: UUID) -> Optional[GraphNode]:
        """
        Retrieves a node by its unique identifier. Returns None if not found.
        """
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: UUID) -> List[GraphNode]:
        """
        Retrieves a list of adjacent nodes connected via outgoing edges from the given node.

        Raises:
            ValueError: If the origin node_id does not exist in the graph.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist in the graph.")

        neighbors: List[GraphNode] = []
        for edge in self.edges:
            if edge.source_node == node_id:
                # Target node is guaranteed to exist due to validation in add_edge()
                neighbors.append(self.nodes[edge.target_node])

        return neighbors

    def list_nodes(self) -> List[GraphNode]:
        """
        Returns a list of all nodes currently registered in the graph.
        """
        return list(self.nodes.values())

    def list_edges(self) -> List[GraphEdge]:
        """
        Returns a list of all edges currently registered in the graph.
        """
        return list(self.edges)
