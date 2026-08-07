import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GATv2Conv


class GATv2Model(nn.Module):
    """
    Graph Attention Network v2 (GATv2) architecture for node classification.
    Strictly responsible for graph-based feature transformation and returning logits.
    """

    def __init__(
        self,
        in_dim: int,
        hidden_dim: int,
        out_dim: int,
        edge_dim: int = 3,
        heads: int = 8,
        dropout: float = 0.6,
    ):
        super(GATv2Model, self).__init__()

        self.dropout_rate = dropout

        # First GATv2 layer: Note that the output dimension will be hidden_dim * heads due to concatenation
        self.conv1 = GATv2Conv(
            in_channels=in_dim,
            out_channels=hidden_dim,
            heads=heads,
            dropout=self.dropout_rate,
            edge_dim=edge_dim,
            concat=True,
        )

        # Second GATv2 layer: The output layer for classification.
        # concat=False averages the attention heads instead of concatenating them.
        self.conv2 = GATv2Conv(
            in_channels=hidden_dim * heads,
            out_channels=out_dim,
            heads=1,
            dropout=self.dropout_rate,
            edge_dim=edge_dim,
            concat=False,
        )

    def forward(self, data: Data) -> torch.Tensor:
        """
        Forward pass over the heterogeneous PyTorch Geometric graph.
        Returns raw, unnormalized logits suitable for CrossEntropyLoss.
        """
        x, edge_index = data.x, data.edge_index
        edge_attr = getattr(data, "edge_attr", None)

        # Dropouts applied to input features
        x = F.dropout(x, p=self.dropout_rate, training=self.training)
        x = self.conv1(x, edge_index, edge_attr=edge_attr)
        x = F.elu(x)

        # Dropouts applied to hidden representations
        x = F.dropout(x, p=self.dropout_rate, training=self.training)
        logits = self.conv2(x, edge_index, edge_attr=edge_attr)

        return logits
