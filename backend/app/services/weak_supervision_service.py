from typing import List

from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset


class WeakSupervisionService:
    """
    Service responsible for applying heuristic labeling functions to generate
    probabilistic pseudo-labels for unlabeled nodes in the TrainingDataset.
    """

    @classmethod
    def generate_pseudo_labels(
        cls, dataset: TrainingDataset, graph: CryptoGraph
    ) -> TrainingDataset:
        """
        Iterates over the dataset and graph. If a node is unlabeled (-1),
        it heuristically uses its contextual risk to generate a pseudo-label,
        preserving exactly any existing human-annotated ground truths.
        """
        sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))

        new_labels: List[int] = []
        pseudo_label_count = 0

        for idx, current_label in enumerate(dataset.node_labels):
            if current_label != -1:
                # Keep exact ground truth
                new_labels.append(current_label)
            else:
                # Unlabeled node: use heuristic weak supervision
                node = sorted_nodes[idx]

                # Heuristic 1: Use contextual_risk if available
                context_risk = node.metadata.get("contextual_risk")
                if context_risk is not None and int(context_risk) > 0:
                    new_labels.append(int(context_risk))
                    pseudo_label_count += 1
                else:
                    # Heuristic 2: Default fallback for completely isolated, un-risky nodes
                    new_labels.append(0)
                    pseudo_label_count += 1

        new_metadata = dict(dataset.metadata)
        new_metadata["weak_supervision_applied"] = True
        new_metadata["pseudo_labels_generated"] = pseudo_label_count

        return TrainingDataset(
            dataset_id=dataset.dataset_id,
            project_id=dataset.project_id,
            generated_at=dataset.generated_at,
            total_nodes=dataset.total_nodes,
            total_edges=dataset.total_edges,
            node_features=dataset.node_features,
            edge_index=dataset.edge_index,
            node_labels=new_labels,
            metadata=new_metadata,
        )
