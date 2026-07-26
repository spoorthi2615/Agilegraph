import torch
from torch_geometric.data import Data
from app.models.training_dataset import TrainingDataset

class GraphDatasetWrapper:
    """
    Wraps the domain TrainingDataset and converts it into a PyTorch Geometric Data object.
    Responsibility strictly limited to tensor conversion. Does not compute metrics or train models.
    """
    @staticmethod
    def to_pyg_data(dataset: TrainingDataset) -> Data:
        """
        Converts the validated TrainingDataset into a PyTorch Geometric Data object.
        """
        # Convert node features to a [num_nodes, num_features] tensor
        x = torch.tensor(dataset.node_features, dtype=torch.float)
        
        # Convert edge index to a [2, num_edges] tensor
        if dataset.edge_index:
            src = [edge[0] for edge in dataset.edge_index]
            dst = [edge[1] for edge in dataset.edge_index]
            edge_index = torch.tensor([src, dst], dtype=torch.long)
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)
            
        # Convert node labels to a [num_nodes] tensor
        y = torch.tensor(dataset.node_labels, dtype=torch.long)
        
        # Build PyG Data object
        data = Data(x=x, edge_index=edge_index, y=y)
        
        # Apply boolean masks if pre-calculated
        if dataset.train_mask:
            data.train_mask = torch.tensor(dataset.train_mask, dtype=torch.bool)
        if dataset.val_mask:
            data.val_mask = torch.tensor(dataset.val_mask, dtype=torch.bool)
            
        return data
