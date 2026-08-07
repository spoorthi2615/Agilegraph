from app.models.crypto_graph import CryptoGraph


class GraphRiskPropagationService:
    """
    Computes structural contextual risk by propagating vulnerability scores
    through the topology of the cryptographic dependency graph.
    """

    @classmethod
    def propagate_risk(cls, graph: CryptoGraph) -> None:
        """
        Calculates and injects the 'contextual_risk' property into every FILE node
        based on the maximum risk score of its structurally contained cryptographic assets.
        Mutates the provided CryptoGraph in-place.
        """
        # Step 1: Identify all FILE nodes in the graph
        file_nodes = [node for node in graph.nodes.values() if node.node_type == "FILE"]

        # Step 2: Traverse topological connections to calculate contextual risk
        for file_node in file_nodes:
            max_risk = 0

            # Find all outgoing CONTAINS edges originating from this specific file
            contains_edges = [
                edge
                for edge in graph.edges
                if edge.source_node == file_node.node_id and edge.edge_type == "CONTAINS"
            ]

            # Retrieve the connected CRYPTO_ASSET nodes and extract their objective risk scores
            for edge in contains_edges:
                target_node = graph.nodes.get(edge.target_node)
                if target_node and target_node.metadata:
                    # Safely default to 0 if an asset somehow bypassed the RiskScoringService
                    risk = target_node.metadata.get("risk_score", 0)
                    if risk > max_risk:
                        max_risk = risk

            # Step 3: Inject the computed contextual risk back into the file's metadata payload
            if file_node.metadata is None:
                file_node.metadata = {}

            file_node.metadata["contextual_risk"] = max_risk
