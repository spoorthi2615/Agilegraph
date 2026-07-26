import torch
import torch.nn as nn
import logging
import time

from app.ml.config.training_config import TrainingConfig
from app.ml.models.gatv2_model import GATv2Model
from app.ml.training.early_stopping import EarlyStopping
from app.ml.training.checkpoint_manager import CheckpointManager
from app.ml.utils.metrics import compute_metrics
from torch_geometric.data import Data

class GATv2Trainer:
    """
    Core orchestrator for GATv2 model training.
    Strictly isolated from data generation and domain logic.
    """
    def __init__(self, config: TrainingConfig):
        self.config = config
        
        # Reproducibility
        torch.manual_seed(self.config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.seed)
            
        self.device = torch.device(self.config.device)
        
        # Initialize model (dimension will be adjusted dynamically upon receiving data)
        self.model = GATv2Model(
            in_dim=1, 
            hidden_dim=self.config.hidden_dim,
            out_dim=self.config.out_dim,
            heads=self.config.heads,
            dropout=self.config.dropout
        ).to(self.device)
        
        # Optimization
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        self.criterion = nn.CrossEntropyLoss(ignore_index=-1)
        
        # Utilities
        self.early_stopping = EarlyStopping(
            patience=self.config.patience, 
            min_delta=self.config.min_delta
        )
        self.checkpoint_manager = CheckpointManager()
        
    def _initialize_model_dims(self, data: Data):
        """
        Dynamically initializes input dimension based on the first observed graph dataset.
        """
        in_dim = data.x.shape[1]
        if self.model.conv1.in_channels != in_dim:
            logging.info(f"Dynamically adjusting model input dimension to {in_dim}")
            self.model = GATv2Model(
                in_dim=in_dim,
                hidden_dim=self.config.hidden_dim,
                out_dim=self.config.out_dim,
                heads=self.config.heads,
                dropout=self.config.dropout
            ).to(self.device)
            self.optimizer = torch.optim.Adam(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )

    def train(self, train_data: Data, val_data: Data):
        """
        Executes the complete training and validation loops.
        """
        self._initialize_model_dims(train_data)
        
        train_data = train_data.to(self.device)
        val_data = val_data.to(self.device)
        
        logging.info(f"Starting GATv2 Training Pipeline on {self.device.type.upper()}...")
        
        for epoch in range(1, self.config.epochs + 1):
            start_time = time.time()
            
            # --- Training Loop ---
            self.model.train()
            self.optimizer.zero_grad()
            
            out = self.model(train_data)
            
            if hasattr(train_data, 'train_mask') and train_data.train_mask is not None:
                train_loss = self.criterion(out[train_data.train_mask], train_data.y[train_data.train_mask])
            else:
                train_loss = self.criterion(out, train_data.y)
                
            train_loss.backward()
            self.optimizer.step()
            
            # --- Validation Loop ---
            self.model.eval()
            with torch.no_grad():
                val_out = self.model(val_data)
                
                if hasattr(val_data, 'val_mask') and val_data.val_mask is not None:
                    val_loss = self.criterion(val_out[val_data.val_mask], val_data.y[val_data.val_mask])
                    acc, prec, rec, f1 = compute_metrics(val_out[val_data.val_mask], val_data.y[val_data.val_mask])
                else:
                    val_loss = self.criterion(val_out, val_data.y)
                    acc, prec, rec, f1 = compute_metrics(val_out, val_data.y)
                    
            elapsed_time = time.time() - start_time
            
            # Early Stopping & Checkpointing
            self.early_stopping(val_loss.item(), self.model)
            if self.early_stopping.best_loss == val_loss.item():
                self.checkpoint_manager.save_checkpoint(
                    self.model, self.optimizer, epoch, val_loss.item()
                )
                checkpoint_msg = "Yes"
            else:
                checkpoint_msg = "No"
                
            # Structured Logging
            logging.info(
                f"\nEpoch {epoch}/{self.config.epochs}\n"
                f"Training Loss: {train_loss.item():.4f}\n"
                f"Validation Loss: {val_loss.item():.4f}\n"
                f"Accuracy: {acc:.4f}\n"
                f"Precision: {prec:.4f}\n"
                f"Recall: {rec:.4f}\n"
                f"F1-score: {f1:.4f}\n"
                f"Checkpoint Saved: {checkpoint_msg}\n"
                f"Elapsed Time: {elapsed_time:.2f}s\n"
            )
            
            if self.early_stopping.early_stop:
                break
                
        # Post-training: Restore best weights
        self.early_stopping.restore_best_weights(self.model)
        logging.info("Training pipeline completed successfully.")
