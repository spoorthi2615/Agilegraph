import os
import sys
import torch
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.training_dataset import TrainingDataset
from app.ml.config.training_config import TrainingConfig
from app.ml.datasets.graph_dataset import GraphDatasetWrapper
from app.ml.training.trainer import GATv2Trainer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint58():
    logging.info("Testing Dataset Wrapper & Tensor Dimensions...")
    
    # 1. Create mock domain dataset
    domain_dataset = TrainingDataset(
        project_id="mock_project",
        total_nodes=4,
        total_edges=4,
        node_features=[
            [1.0, 0.0, 0.5],
            [0.0, 1.0, 0.2],
            [0.5, 0.5, 0.9],
            [0.1, 0.9, 0.1]
        ],
        edge_index=[(0, 1), (1, 2), (2, 3), (3, 0)],
        node_labels=[0, 1, 2, 3],
        train_mask=[True, True, False, False],
        val_mask=[False, False, True, True]
    )
    
    # 2. Verify wrapper
    pyg_data = GraphDatasetWrapper.to_pyg_data(domain_dataset)
    
    assert pyg_data.x.shape == (4, 3), f"Feature shape mismatch: {pyg_data.x.shape}"
    assert pyg_data.edge_index.shape == (2, 4), f"Edge shape mismatch: {pyg_data.edge_index.shape}"
    assert pyg_data.y.shape == (4,), f"Label shape mismatch: {pyg_data.y.shape}"
    
    logging.info("Testing Trainer, Model Forward/Backward, Early Stopping, Metrics, and Checkpointing...")
    
    # 3. Setup trainer with tiny epochs
    config = TrainingConfig(
        epochs=3,
        hidden_dim=16,
        heads=2,
        device="cpu"
    )
    
    trainer = GATv2Trainer(config)
    
    # 4. Run training (which encompasses forward, backward, metrics, checkpointing)
    trainer.train(pyg_data, pyg_data)
    
    # 5. Verify checkpoint was created
    assert os.path.exists("outputs/models/gatv2_best.pt"), "Checkpoint failed to save."
    
    logging.info("All Sprint 58 ML Pipeline components executed successfully!")

if __name__ == "__main__":
    test_sprint58()
