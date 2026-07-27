from typing import Any, List
import time
import logging
from datetime import datetime, timezone

from app.models.training_dataset import TrainingDataset
from app.models.dataset_validation import DatasetValidation
from app.models.model_config import ModelConfig
from app.models.training_result import TrainingResult

logger = logging.getLogger(__name__)

# Safely handle heavy ML dependencies to ensure CI/CD and edge environments don't crash
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class GATv2TrainingService:
    """
    Service responsible for executing the mathematical optimization process (training loop)
    for an initialized GATv2 model using a strictly validated TrainingDataset.
    """

    @classmethod
    def train_model(
        cls, 
        dataset: TrainingDataset, 
        validation: DatasetValidation, 
        config: ModelConfig, 
        model: Any,
        training_config: Any = None,
        epochs: int = 100
    ) -> TrainingResult:
        """
        Executes backpropagation over the graph dataset to optimize model weights.
        Strictly restricted to training; evaluation and inference are explicitly excluded.
        """
        if training_config is None:
            from app.models.training_config import TrainingConfig
            training_config = TrainingConfig()
        # 1. Verify Dataset Validation mathematically
        if not validation.validation_passed:
            raise ValueError(
                f"Training aborted. Dataset {dataset.dataset_id} failed architectural validation. "
                f"Integrity Errors: {validation.validation_messages}"
            )
            
        # 2. Verify Model Compatibility
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch framework unavailable. Returning symbolic TrainingResult bypass.")
            return cls._simulate_training(dataset, config, epochs, training_config.learning_rate)
            
        if not isinstance(model, nn.Module):
            raise TypeError("Provided model instance is not a valid PyTorch nn.Module. Cannot execute training loop.")
            
        # Convert primitive lists into PyTorch Tensors
        x_tensor = torch.tensor(dataset.node_features, dtype=torch.float)
        
        # GNNs require Edge Index in Coordinate Format (COO) of shape [2, num_edges]
        if not dataset.edge_index:
            raise ValueError("TrainingDataset contains no topological edges. Message passing is impossible.")
            
        src_list = [edge[0] for edge in dataset.edge_index]
        tgt_list = [edge[1] for edge in dataset.edge_index]
        edge_index_tensor = torch.tensor([src_list, tgt_list], dtype=torch.long)
        
        # Convert Node Labels (Classification task: 0 = Safe, 1 = Vulnerable)
        y_tensor = torch.tensor(dataset.node_labels, dtype=torch.long)
        
        # Handle train/validation masks securely
        if dataset.val_mask and len(dataset.val_mask) == len(dataset.node_labels):
            train_mask = torch.tensor(dataset.train_mask, dtype=torch.bool)
            val_mask = torch.tensor(dataset.val_mask, dtype=torch.bool)
        else:
            # Fallback: train and validate on all nodes if splits are missing
            train_mask = torch.ones(len(dataset.node_labels), dtype=torch.bool)
            val_mask = torch.ones(len(dataset.node_labels), dtype=torch.bool)
            
        # 3. Initialize Optimizer from Configuration
        if training_config.optimizer_type.upper() == "SGD":
            optimizer = optim.SGD(model.parameters(), lr=training_config.learning_rate, weight_decay=training_config.weight_decay)
        else:
            optimizer = optim.Adam(model.parameters(), lr=training_config.learning_rate, weight_decay=training_config.weight_decay)
        
        # 4. Initialize Loss Function (Classification)
        criterion = nn.CrossEntropyLoss()
            
        # 5. Initialize Early Stopping and Checkpointing Services
        from app.services.early_stopping_service import EarlyStoppingService
        from app.services.model_checkpoint_service import ModelCheckpointService
        
        early_stopper = EarlyStoppingService(patience=training_config.patience)
        
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        loss_history: List[float] = []
        
        # 6. Execute Training Loop
        for epoch in range(epochs):
            model.train()
            optimizer.zero_grad()
            
            # Forward Pass
            out = model(x_tensor, edge_index_tensor)
            
            # Compute Loss on training nodes only
            loss = criterion(out[train_mask], y_tensor[train_mask])
            loss.backward()
            optimizer.step()
            
            # Validation Step
            model.eval()
            with torch.no_grad():
                val_out = model(x_tensor, edge_index_tensor)
                val_loss = criterion(val_out[val_mask], y_tensor[val_mask])
                
            loss_history.append(float(val_loss.item()))
            
            # Convergence Monitoring & Checkpointing
            if early_stopper.step(float(val_loss.item())):
                ModelCheckpointService.save_checkpoint(model, training_config.checkpoint_path)
                
            if early_stopper.early_stop:
                break
                
        # Load best weights before returning
        ModelCheckpointService.load_checkpoint(model, training_config.checkpoint_path)
        
        # 7. Measure Training Duration
        end_time = time.perf_counter()
        completed_at = datetime.now(timezone.utc)
        
        duration = end_time - start_time
        final_loss = loss_history[-1] if loss_history else 0.0
        
        # 8. Return comprehensive TrainingResult
        return TrainingResult(
            model_id=config.model_id,
            dataset_id=dataset.dataset_id,
            started_at=started_at,
            completed_at=completed_at,
            epochs=epochs,
            learning_rate=training_config.learning_rate,
            optimizer=training_config.optimizer_type,
            loss_history=loss_history,
            final_training_loss=final_loss,
            training_duration_seconds=duration,
            training_completed=True,
            metadata={
                "device": "cpu",
                "loss_function": "CrossEntropyLoss"
            }
        )

    @classmethod
    def _simulate_training(
        cls, 
        dataset: TrainingDataset, 
        config: ModelConfig, 
        epochs: int, 
        learning_rate: float
    ) -> TrainingResult:
        """
        Creates a symbolic, bypassed TrainingResult for lightweight environments 
        where the massive PyTorch binaries are intentionally excluded.
        """
        now = datetime.now(timezone.utc)
        return TrainingResult(
            model_id=config.model_id,
            dataset_id=dataset.dataset_id,
            started_at=now,
            completed_at=now,
            epochs=epochs,
            learning_rate=learning_rate,
            optimizer="Adam (Symbolic)",
            loss_history=[0.0] * epochs,
            final_training_loss=0.0,
            training_duration_seconds=0.0,
            training_completed=False,
            metadata={"status": "Symbolic bypass - PyTorch framework not installed."}
        )
