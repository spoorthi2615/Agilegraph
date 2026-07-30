from typing import Any
import logging
from app.models.model_config import ModelConfig
from app.models.training_dataset import TrainingDataset

logger = logging.getLogger(__name__)

# Safely attempt to load heavy ML frameworks. 
# This maintains application stability in lightweight scanner environments (Docker) 
# that intentionally exclude PyTorch to save gigabytes of space.
try:
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.nn import GATv2Conv
    
    class GATv2NodeClassifier(nn.Module):
        """
        Native PyTorch Geometric implementation of a Graph Attention Network v2.
        Operates strictly as a structural architecture without embedded training logic.
        """
        def __init__(self, config: ModelConfig):
            super().__init__()
            self.config = config
            
            # Layer 1: Input feature space to Hidden dimension
            self.conv1 = GATv2Conv(
                in_channels=config.input_dimension,
                out_channels=config.hidden_dimension,
                heads=config.attention_heads,
                concat=True,
                dropout=config.dropout
            )
            
            # Layer 2: Hidden dimension to Output prediction space
            # Because concat=True in Layer 1, the hidden size is multiplied by the number of heads
            self.conv2 = GATv2Conv(
                in_channels=config.hidden_dimension * config.attention_heads,
                out_channels=config.output_dimension,
                heads=1, # Usually 1 head for the final prediction output
                concat=False,
                dropout=config.dropout
            )
            
        def forward(self, x, edge_index):
            # Message Passing Layer 1
            x = F.dropout(x, p=self.config.dropout, training=self.training)
            x = self.conv1(x, edge_index)
            
            # Non-linear Activation
            if self.config.activation == "ELU":
                x = F.elu(x)
            else:
                x = F.relu(x)
                
            # Message Passing Layer 2
            x = F.dropout(x, p=self.config.dropout, training=self.training)
            x = self.conv2(x, edge_index)
            
            return x

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class GATv2ModelService:
    """
    Service responsible for validating dimensional constraints and initializing 
    the GATv2 architecture based on the extracted TrainingDataset features.
    """

    @classmethod
    def initialize_model(cls, dataset: TrainingDataset, config: ModelConfig) -> Any:
        """
        Validates feature dimensions against the config and builds the GATv2 architecture.
        Returns the initialized PyTorch module (if available) or a symbolic representation.
        """
        # 1. Validate Feature Dimensions
        if not dataset.node_features:
            raise ValueError("TrainingDataset contains no node features. Cannot initialize model.")
            
        dataset_dim = len(dataset.node_features[0])
        if dataset_dim != config.input_dimension:
            raise ValueError(
                f"Dimensionality mismatch: Dataset extracts {dataset_dim} features per node, "
                f"but ModelConfig expects exactly {config.input_dimension} input dimensions."
            )
            
        # 2. Build the GATv2 Architecture
        if TORCH_AVAILABLE:
            logger.info(f"Initializing native PyTorch GATv2 architecture with {config.input_dimension} input dims.")
            return GATv2NodeClassifier(config)
        else:
            # Fallback for core backend environments where PyTorch is intentionally excluded
            logger.warning("PyTorch Geometric is not installed. Returning symbolic model initialization.")
            return {
                "status": "Initialized Symbolically",
                "architecture": "GATv2NodeClassifier",
                "hyperparameters": config.model_dump(),
                "ready_for_training": False
            }
