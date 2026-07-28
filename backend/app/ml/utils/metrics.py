import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

def compute_metrics(logits: torch.Tensor, labels: torch.Tensor):
    """
    Computes multi-class classification metrics: Accuracy, Precision, Recall, F1-score.
    Calculates macro-averaged metrics across all classes.
    Automatically filters out any unlabeled (-1) nodes if they exist.
    """
    preds = logits.argmax(dim=1)
    
    # Filter out unlabeled nodes
    mask = labels != -1
    preds_filtered = preds[mask].cpu().numpy()
    targets_filtered = labels[mask].cpu().numpy()
    
    if len(targets_filtered) == 0:
        return 0.0, 0.0, 0.0, 0.0, "No labeled nodes found in this split."
        
    accuracy = accuracy_score(targets_filtered, preds_filtered)
    macro_precision = precision_score(targets_filtered, preds_filtered, average='macro', zero_division=0)
    macro_recall = recall_score(targets_filtered, preds_filtered, average='macro', zero_division=0)
    macro_f1 = f1_score(targets_filtered, preds_filtered, average='macro', zero_division=0)
    
    report_string = classification_report(targets_filtered, preds_filtered, zero_division=0)
        
    return accuracy, macro_precision, macro_recall, macro_f1, report_string
