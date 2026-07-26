from typing import List, Dict, Tuple
from uuid import UUID
from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph
from app.models.project_analysis import ProjectAnalysisResult
from app.models.graph_node import GraphNode

class DatasetProcessingService:
    """
    Service responsible for converting the complex, arbitrary object-oriented 
    CryptoGraph domain model into flat, numerically structured arrays ready 
    for ingestion by external Graph Neural Networks (GNNs).
    """

    @classmethod
    def process_graph(
        cls, 
        analysis_result: ProjectAnalysisResult, 
        graph: CryptoGraph
    ) -> TrainingDataset:
        """
        Traverses the graph to assign deterministic integer indices to UUIDs, 
        extracts raw node features, and maps topological edges into integer arrays.
        """
        
        # Step 1: Assign deterministic integer indices to nodes.
        # ML frameworks require nodes to be numbered contiguously (0 to N-1)
        node_to_index: Dict[UUID, int] = {}
        index_to_node: Dict[int, GraphNode] = {}
        
        # Sorting nodes by UUID string ensures absolute determinism across executions
        sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))
        
        for idx, node in enumerate(sorted_nodes):
            node_to_index[node.node_id] = idx
            index_to_node[idx] = node
            
        # Step 2: Generate node features (X) and node labels (Y)
        node_features: List[List[float]] = []
        node_labels: List[int] = []
        
        for idx in range(len(sorted_nodes)):
            node = index_to_node[idx]
            
            # Extract basic raw numerical features without normalizing or generating embeddings
            is_file = 1.0 if node.node_type == "FILE" else 0.0
            is_dependency = 1.0 if node.node_type == "DEPENDENCY" else 0.0
            contextual_risk = float(node.metadata.get("contextual_risk", 0.0))
            
            features = [is_file, is_dependency, contextual_risk]
            node_features.append(features)
            
            # Ground truth label: the base risk score (used as the prediction target)
            risk_score = int(node.metadata.get("risk_score", 0))
            node_labels.append(risk_score)
            
        # Step 3: Generate edge index for structural topology
        # Converts arbitrary UUID connections into strict integer coordinate pairs
        edge_index: List[Tuple[int, int]] = []
        
        for edge in graph.edges:
            source_idx = node_to_index.get(edge.source_node)
            target_idx = node_to_index.get(edge.target_node)
            
            if source_idx is not None and target_idx is not None:
                edge_index.append((source_idx, target_idx))
                
        # Step 4: Populate traceability metadata
        # Crucial for mapping the ML predictions back to the actual files/assets
        metadata = {
            "node_index_mapping": {str(uid): idx for uid, idx in node_to_index.items()},
            "feature_columns": ["is_file", "is_dependency", "contextual_risk"],
            "label_description": "risk_score"
        }
        
        return TrainingDataset(
            project_id=analysis_result.project_id,
            total_nodes=len(sorted_nodes),
            total_edges=len(edge_index),
            node_features=node_features,
            edge_index=edge_index,
            node_labels=node_labels,
            metadata=metadata
        )
