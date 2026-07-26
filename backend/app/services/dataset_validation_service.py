from collections import Counter
from typing import List, Set
from app.models.training_dataset import TrainingDataset
from app.models.dataset_validation import DatasetValidation

class DatasetValidationService:
    """
    Service responsible for strictly verifying the mathematical integrity of a 
    TrainingDataset before it is exported for Graph Neural Network ingestion.
    """

    @classmethod
    def validate(cls, dataset: TrainingDataset) -> DatasetValidation:
        """
        Executes a deterministic ruleset to verify tensor dimensions, edge bounds, 
        and label distributions without mutating the dataset.
        """
        messages: List[str] = []
        is_valid = True
        
        # 1. Verify Equal Feature Dimensions (Uniform Matrix)
        if not dataset.node_features:
            messages.append("Dataset contains no node features.")
            is_valid = False
            feature_dim = 0
        else:
            feature_dim = len(dataset.node_features[0])
            for idx, f_vec in enumerate(dataset.node_features):
                if len(f_vec) != feature_dim:
                    messages.append(f"Inconsistent feature dimension at node index {idx}. Expected {feature_dim}, got {len(f_vec)}.")
                    is_valid = False
                    
        # 2. Verify Correct Label Count (Y-vector length)
        if len(dataset.node_labels) != dataset.total_nodes:
            messages.append(f"Label count mismatch. Expected {dataset.total_nodes}, got {len(dataset.node_labels)}.")
            is_valid = False
            
        # 3. Verify Valid Edge Indices and Report Isolated Nodes
        connected_nodes: Set[int] = set()
        for edge_idx, (src, tgt) in enumerate(dataset.edge_index):
            if src < 0 or src >= dataset.total_nodes or tgt < 0 or tgt >= dataset.total_nodes:
                messages.append(f"Malformed edge at index {edge_idx}: ({src}, {tgt}) references out-of-bounds nodes.")
                is_valid = False
            else:
                connected_nodes.add(src)
                connected_nodes.add(tgt)
                
        isolated_nodes = dataset.total_nodes - len(connected_nodes)
        if isolated_nodes > 0:
            # Isolated nodes do not inherently fail validation (they are valid graph states),
            # but they degrade message-passing efficiency in GNNs and must be logged.
            messages.append(f"Detected {isolated_nodes} isolated nodes with no topological connections.")
            
        # 4. Generate Label Distribution for Class Imbalance Detection
        label_counts = Counter(dataset.node_labels)
        label_distribution = {str(k): v for k, v in label_counts.items()}
        
        if is_valid:
            messages.append("Dataset passed all mathematical integrity checks.")
            
        return DatasetValidation(
            dataset_id=dataset.dataset_id,
            total_nodes=dataset.total_nodes,
            total_edges=dataset.total_edges,
            feature_dimension=feature_dim,
            label_distribution=label_distribution,
            isolated_nodes=isolated_nodes,
            validation_passed=is_valid,
            validation_messages=messages
        )
