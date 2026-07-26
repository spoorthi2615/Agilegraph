from typing import Any
import time
import logging
from datetime import datetime, timezone

from app.models.training_result import TrainingResult
from app.models.training_dataset import TrainingDataset
from app.models.model_config import ModelConfig
from app.models.evaluation_result import EvaluationResult

logger = logging.getLogger(__name__)

# Safely handle heavy ML dependencies
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Scikit-learn for advanced metrics if available
try:
    from sklearn.metrics import roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class GATv2EvaluationService:
    """
    Service responsible for strictly evaluating the predictive performance of a 
    trained GATv2 neural network against an unseen dataset.
    """

    @classmethod
    def evaluate_model(
        cls,
        training_result: TrainingResult,
        model: Any,
        dataset: TrainingDataset,
        config: ModelConfig
    ) -> EvaluationResult:
        """
        Executes a deterministic forward pass over the evaluation dataset with gradients disabled,
        computes the testing loss, and mathematically derives classification accuracy metrics.
        """
        # 1. Verify Training Completed
        if not training_result.training_completed:
            raise ValueError("Evaluation aborted: The provided model has not successfully completed training.")
            
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        # 2. Check Compatibility
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch framework unavailable. Returning symbolic EvaluationResult bypass.")
            return cls._simulate_evaluation(training_result, dataset, config)
            
        if not isinstance(model, nn.Module):
            raise TypeError("Provided model instance is not a valid PyTorch nn.Module. Cannot evaluate.")
            
        # 3. Setup Testing Tensors
        x_tensor = torch.tensor(dataset.node_features, dtype=torch.float)
        
        if not dataset.edge_index:
            raise ValueError("Evaluation Dataset contains no topological edges. Message passing is impossible.")
            
        src_list = [edge[0] for edge in dataset.edge_index]
        tgt_list = [edge[1] for edge in dataset.edge_index]
        edge_index_tensor = torch.tensor([src_list, tgt_list], dtype=torch.long)
        
        # Ground truth risk labels
        y_tensor = torch.tensor(dataset.node_labels, dtype=torch.float).view(-1, 1)
        criterion = nn.MSELoss()
        
        # 4. Switch Model to Evaluation Mode (Disables Dropout and BatchNorm adjustments)
        model.eval()
        
        # 5. Disable Gradients (Crucial to prevent modifying neural weights during testing)
        with torch.no_grad():
            
            # 6. Execute Forward Pass on unseen data
            out = model(x_tensor, edge_index_tensor)
            
            # 7. Compute Evaluation Loss
            loss = criterion(out, y_tensor)
            eval_loss = float(loss.item())
            
            # 8. Generate Predictions (Thresholding regression output into Binary Classification)
            # Assuming ground truth risk_score >= 75 is Class 1 (High Risk), else Class 0
            y_true_binary = (y_tensor >= 75.0).float()
            
            probs = torch.sigmoid(out)
            preds = (probs >= 0.5).float()
            
        # 9. Calculate Mathematical Metrics
        y_true_np = y_true_binary.cpu().numpy()
        preds_np = preds.cpu().numpy()
        probs_np = probs.cpu().numpy()
        
        # Derive Confusion Matrix quadrants manually to avoid strictly requiring scikit-learn
        tp = float(((preds_np == 1) & (y_true_np == 1)).sum())
        fp = float(((preds_np == 1) & (y_true_np == 0)).sum())
        tn = float(((preds_np == 0) & (y_true_np == 0)).sum())
        fn = float(((preds_np == 0) & (y_true_np == 1)).sum())
        
        accuracy = (tp + tn) / max((tp + tn + fp + fn), 1.0)
        precision = tp / max((tp + fp), 1.0)
        recall = tp / max((tp + fn), 1.0)
        f1 = 2 * (precision * recall) / max((precision + recall), 1e-7)
        
        confusion_matrix = [
            [int(tn), int(fp)], # Top row: [True Negative, False Positive]
            [int(fn), int(tp)]  # Bottom row: [False Negative, True Positive]
        ]
        
        # ROC-AUC calculation (only computed if sklearn is present and multiple classes exist)
        auc_score = 0.0
        if SKLEARN_AVAILABLE:
            try:
                if len(set(y_true_np.flatten())) > 1:
                    auc_score = float(roc_auc_score(y_true_np, probs_np))
            except Exception as e:
                logger.warning(f"Could not calculate ROC-AUC: {e}")
                
        # 10. Measure Evaluation Duration
        end_time = time.perf_counter()
        completed_at = datetime.now(timezone.utc)
        duration = end_time - start_time
        
        # 11. Return final EvaluationResult
        return EvaluationResult(
            training_id=training_result.training_id,
            model_id=config.model_id,
            dataset_id=dataset.dataset_id,
            evaluated_at=completed_at,
            evaluation_loss=eval_loss,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_score=auc_score,
            confusion_matrix=confusion_matrix,
            evaluation_duration_seconds=duration,
            evaluation_completed=True,
            metadata={"classification_threshold": 75.0, "sklearn_available": SKLEARN_AVAILABLE}
        )
        
    @classmethod
    def _simulate_evaluation(
        cls, 
        training_result: TrainingResult, 
        dataset: TrainingDataset, 
        config: ModelConfig
    ) -> EvaluationResult:
        """
        Creates a symbolic, bypassed EvaluationResult for lightweight environments 
        where the PyTorch binaries are intentionally excluded.
        """
        now = datetime.now(timezone.utc)
        return EvaluationResult(
            training_id=training_result.training_id,
            model_id=config.model_id,
            dataset_id=dataset.dataset_id,
            evaluated_at=now,
            evaluation_loss=0.0,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            auc_score=0.0,
            confusion_matrix=[[0, 0], [0, 0]],
            evaluation_duration_seconds=0.0,
            evaluation_completed=False,
            metadata={"status": "Symbolic bypass - PyTorch framework not installed."}
        )
