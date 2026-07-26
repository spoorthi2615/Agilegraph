from typing import List
from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph

class LabelGenerationService:
    """
    Service strictly responsible for extracting exact ground-truth labels 
    from the CryptoGraph and injecting them into the TrainingDataset.
    Does not perform any topology mapping or feature engineering.
    """
    
    @classmethod
    def generate_labels(cls, dataset: TrainingDataset, graph: CryptoGraph) -> TrainingDataset:
        sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))
        
        node_labels: List[int] = []
        for node in sorted_nodes:
            # -1 represents an unlabeled node, to be picked up by WeakSupervisionService
            risk_score = node.metadata.get("risk_score")
            if risk_score is not None:
                node_labels.append(int(risk_score))
            else:
                node_labels.append(-1)
                
        new_metadata = dict(dataset.metadata)
        new_metadata["label_description"] = "risk_score"
        
        return TrainingDataset(
            dataset_id=dataset.dataset_id,
            project_id=dataset.project_id,
            generated_at=dataset.generated_at,
            total_nodes=dataset.total_nodes,
            total_edges=dataset.total_edges,
            node_features=dataset.node_features,
            edge_index=dataset.edge_index,
            node_labels=node_labels,
            metadata=new_metadata
        )
