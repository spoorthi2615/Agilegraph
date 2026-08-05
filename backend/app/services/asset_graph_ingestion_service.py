import uuid
from typing import List, Dict, Any

from app.models.crypto_graph import CryptoGraph
from app.models.graph_node import GraphNode
from app.models.graph_edge import GraphEdge
from app.services.neo4j_export_service import Neo4jExportService
from app.config.settings import settings

class AssetGraphIngestionService:
    @staticmethod
    def ingest_certificates(
        project_id: str,
        parsed_certs: List[Dict[str, Any]],
        user_id: str = None,
        owner_email: str = None,
    ) -> None:
        """
        Converts parsed certificates directly into GraphNodes and pushes them to Neo4j.
        """
        graph = CryptoGraph()
        
        for idx, cert in enumerate(parsed_certs):
            # Create a Certificate Node
            cert_node_id = uuid.uuid4()
            cert_node = GraphNode(
                node_id=cert_node_id,
                node_type="CERTIFICATE",
                label=f"Certificate: {cert.get('subject', 'Unknown')}",
                metadata={
                    "issuer": cert.get('issuer'),
                    "not_before": cert.get('not_before'),
                    "not_after": cert.get('not_after'),
                    "source": cert.get('source', 'Upload'),
                    "project_id": project_id
                }
            )
            graph.add_node(cert_node)
            
            # Create an Algorithm Node
            algo_name = cert.get('algorithm', 'Unknown')
            key_size = cert.get('key_size', 0)
            
            # Basic risk scoring for certs
            risk_score = 0
            severity = "low"
            if algo_name in ["RSA", "DSA", "ECDSA"]:
                risk_score = 85
                severity = "high"
                
            algo_node_id = uuid.uuid4()
            algo_node = GraphNode(
                node_id=algo_node_id,
                node_type="CRYPTO_ASSET",
                label=f"{algo_name} ({key_size} bit)",
                metadata={
                    "algorithm": algo_name,
                    "key_size": key_size,
                    "risk_score": risk_score,
                    "severity": severity,
                    "project_id": project_id,
                    "asset_type": "Public Key Algorithm"
                }
            )
            graph.add_node(algo_node)
            
            # Create Edge: Certificate -> IMPLEMENTS -> Algorithm
            edge = GraphEdge(
                source_node=cert_node_id,
                target_node=algo_node_id,
                edge_type="IMPLEMENTS"
            )
            graph.add_edge(edge)
            
        export_service = Neo4jExportService(
            settings.NEO4J_URI, settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD
        )
        try:
            export_service.export_graph(graph, user_id=user_id, owner_email=owner_email)
        finally:
            export_service.close()
