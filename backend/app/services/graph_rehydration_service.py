from uuid import UUID
from app.models.crypto_graph import CryptoGraph
from app.models.graph_node import GraphNode
from app.models.graph_edge import GraphEdge
from app.services.graph_query_service import GraphQueryService

class GraphRehydrationService:
    """
    Responsible for reconstructing a full in-memory CryptoGraph from Neo4j records, 
    bypassing the need for synchronous static analysis re-execution.
    """
    
    def __init__(self, query_service: GraphQueryService) -> None:
        self.query_service = query_service

    def rehydrate_graph(self) -> CryptoGraph:
        """
        Retrieves all nodes and edges from the graph database and rebuilds the 
        CryptoGraph Domain Model natively in memory.
        """
        graph = CryptoGraph()
        
        # Using the existing query_service driver connection
        with self.query_service.driver.session() as session:
            # Step 1: Rehydrate Nodes
            node_result = session.run("MATCH (n) RETURN n")
            for record in node_result:
                n = record["n"]
                props = dict(n)
                
                # Extract identity properties
                node_id_str = props.pop("node_id", None)
                if not node_id_str:
                    continue
                    
                node_type = props.pop("node_type", "UNKNOWN")
                label = props.pop("label", "Unknown")
                
                # Reconstruct flexible metadata payload
                metadata = {}
                for key, val in props.items():
                    metadata[key] = val
                    
                # Explicitly ensure scoring metrics are safely placed in metadata for downstream analytics
                if "risk_score" in props:
                    metadata["risk_score"] = props["risk_score"]
                if "severity" in props:
                    metadata["severity"] = props["severity"]
                    
                node = GraphNode(
                    node_id=UUID(node_id_str),
                    node_type=node_type,
                    label=label,
                    metadata=metadata
                )
                graph.add_node(node)
                
            # Step 2: Rehydrate Relationships (Edges)
            edge_result = session.run("MATCH (a)-[r]->(b) RETURN a.node_id AS source, type(r) AS type, b.node_id AS target")
            for record in edge_result:
                source = record["source"]
                target = record["target"]
                edge_type = record["type"]
                
                if source and target:
                    edge = GraphEdge(
                        source_node=UUID(source),
                        target_node=UUID(target),
                        edge_type=edge_type,
                        metadata={}
                    )
                    graph.add_edge(edge)
                    
        return graph
