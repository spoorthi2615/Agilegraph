import torch

class ROCMetrics:
    """
    Computes ROC-AUC dynamically using probabilities.
    Requires sklearn, but gracefully fails over to None if the batch contains 
    only a single class or if sklearn is unavailable.
    """
    @staticmethod
    def compute(probs: torch.Tensor, targets: torch.Tensor, num_classes: int) -> float | None:
        try:
            from sklearn.metrics import roc_auc_score
            import numpy as np
            
            y_true = targets.cpu().numpy()
            y_scores = probs.cpu().numpy()
            
            # Ensure multiple classes exist in true labels to prevent ROC calculation errors
            if len(np.unique(y_true)) <= 1:
                return None
                
            # Use 'ovr' (One-vs-Rest) and macro averaging for multiclass
            auc = roc_auc_score(y_true, y_scores, multi_class='ovr', average='macro')
            return float(auc)
        except Exception:
            # Gracefully handle any failure (e.g. sklearn not installed)
            return None
