from typing import Any, Dict

from neo4j import GraphDatabase, Transaction

from app.models.crypto_graph import CryptoGraph


class Neo4jExportService:
    """
    Exports the in-memory CryptoGraph structural representation into a physical Neo4j database.
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def export_graph(
        self, graph: CryptoGraph, user_id: str = None, owner_email: str = None
    ) -> None:
        """
        Executes the entire graph export within a managed Neo4j session.
        """
        with self.driver.session() as session:
            session.execute_write(self._export_transaction, graph, user_id, owner_email)

    @staticmethod
    def _export_transaction(
        tx: Transaction, graph: CryptoGraph, user_id: str = None, owner_email: str = None
    ) -> None:
        """
        Internal transaction function. Iterates through all nodes and edges
        and merges them into Neo4j to ensure idempotency.
        """
        # Step 1: Export Nodes
        for _node_id, node in graph.nodes.items():
            # Node Type acts as the Cypher Label (e.g., :FILE, :CRYPTO_ASSET, :DEPENDENCY)
            node_type = node.node_type

            # Base properties
            props: Dict[str, Any] = {
                "node_id": str(node.node_id),
                "label": node.label,
                "node_type": node_type,
            }

            # Flatten metadata into the properties payload.
            # This automatically includes risk_score and severity from the RiskScoringService
            if node.metadata:
                props.update(node.metadata)

            if user_id:
                props["owner_id"] = user_id
            if owner_email:
                props["owner_email"] = owner_email

            # MERGE creates the node if it doesn't exist, based solely on node_id.
            # SET += updates all other properties efficiently.
            query = f"""
            MERGE (n:{node_type} {{node_id: $props.node_id}})
            SET n += $props
            """
            tx.run(query, props=props)

        # Step 2: Export Relationships
        for edge in graph.edges:
            edge_type = edge.edge_type

            # Relationships don't require full deduplication IDs in this schema,
            # we MERGE purely on the specific connection between the two exact node_ids.
            props = {"source_id": str(edge.source_node), "target_id": str(edge.target_node)}

            # Flatten any potential edge metadata
            if edge.metadata:
                # Exclude duplicate structural keys if they exist in metadata
                meta_clean = {
                    k: v for k, v in edge.metadata.items() if k not in ["source_id", "target_id"]
                }
                props.update(meta_clean)

            query = f"""
            MATCH (source {{node_id: $props.source_id}})
            MATCH (target {{node_id: $props.target_id}})
            MERGE (source)-[r:{edge_type}]->(target)
            SET r += $props
            """
            tx.run(query, props=props)
