from typing import List
from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph

class FeatureEngineeringService:
    """
    Service responsible for expanding the basic node feature matrix of a TrainingDataset 
    into a high-dimensional, deterministic mathematical representation for GNN training.
    """

    # Deterministic vocabulary of algorithms for one-hot encoding
    _ALGORITHM_VOCAB = ["AES", "RSA", "MD5", "SHA-1", "SHA-256", "ECC", "EC", "DES", "3DES"]
    
    @classmethod
    def expand_features(cls, dataset: TrainingDataset, graph: CryptoGraph) -> TrainingDataset:
        """
        Calculates and injects a high-dimensional feature vector for each node.
        Returns a newly instantiated TrainingDataset to maintain immutability.
        """
        # Ensure we iterate nodes in the exact same deterministic order as DatasetProcessingService
        sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))
        
        # Pre-calculate topological degree (in-degree + out-degree) for all nodes
        node_degrees = {str(n.node_id): 0 for n in sorted_nodes}
        for edge in graph.edges:
            node_degrees[str(edge.source_node)] += 1
            node_degrees[str(edge.target_node)] += 1
            
        new_node_features: List[List[float]] = []
        
        for node in sorted_nodes:
            feature_vector: List[float] = []
            
            # 1. Node Type Encoding (One-Hot)
            is_file = 1.0 if node.node_type == "FILE" else 0.0
            is_dependency = 1.0 if node.node_type == "DEPENDENCY" else 0.0
            is_asset = 1.0 if node.node_type not in ["FILE", "DEPENDENCY"] else 0.0
            feature_vector.extend([is_file, is_dependency, is_asset])
            
            # 2. Risk and Severity Metrics
            risk_score = float(node.metadata.get("risk_score", 0.0))
            contextual_risk = float(node.metadata.get("contextual_risk", 0.0))
            
            severity_str = str(node.metadata.get("severity", "")).upper()
            sev_critical = 1.0 if severity_str == "CRITICAL" else 0.0
            sev_high = 1.0 if severity_str == "HIGH" else 0.0
            sev_medium = 1.0 if severity_str == "MEDIUM" else 0.0
            sev_low = 1.0 if severity_str == "LOW" else 0.0
            
            feature_vector.extend([risk_score, contextual_risk, sev_critical, sev_high, sev_medium, sev_low])
            
            # 3. Topological Degree
            degree = float(node_degrees[str(node.node_id)])
            feature_vector.append(degree)
            
            # 4. One-Hot Algorithm Encoding
            algo = str(node.metadata.get("algorithm", "")).upper()
            for vocab_word in cls._ALGORITHM_VOCAB:
                feature_vector.append(1.0 if algo == vocab_word else 0.0)
                
            new_node_features.append(feature_vector)
            
        # Update traceability metadata
        new_metadata = dict(dataset.metadata)
        new_metadata["feature_dimension"] = len(new_node_features[0])
        
        return TrainingDataset(
            dataset_id=dataset.dataset_id,
            project_id=dataset.project_id,
            generated_at=dataset.generated_at,
            total_nodes=dataset.total_nodes,
            total_edges=dataset.total_edges,
            node_features=new_node_features,
            edge_index=dataset.edge_index,
            node_labels=dataset.node_labels,
            metadata=new_metadata
        )
