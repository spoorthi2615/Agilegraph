import torch

def compute_metrics(logits: torch.Tensor, labels: torch.Tensor):
    """
    Computes multi-class classification metrics: Accuracy, Precision, Recall, F1-score.
    Calculates macro-averaged metrics across all classes.
    Automatically filters out any unlabeled (-1) nodes if they exist.
    """
    preds = logits.argmax(dim=1)
    
    # Filter out unlabeled nodes
    mask = labels != -1
    preds = preds[mask]
    targets = labels[mask]
    
    if len(targets) == 0:
        return 0.0, 0.0, 0.0, 0.0
        
    correct = (preds == targets).sum().item()
    accuracy = correct / len(targets)
    
    num_classes = logits.shape[1]
    
    precisions = []
    recalls = []
    
    for c in range(num_classes):
        true_positive = ((preds == c) & (targets == c)).sum().item()
        false_positive = ((preds == c) & (targets != c)).sum().item()
        false_negative = ((preds != c) & (targets == c)).sum().item()
        
        p = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0.0
        r = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0.0
        
        precisions.append(p)
        recalls.append(r)
        
    macro_precision = sum(precisions) / num_classes
    macro_recall = sum(recalls) / num_classes
    
    if macro_precision + macro_recall > 0:
        macro_f1 = 2 * (macro_precision * macro_recall) / (macro_precision + macro_recall)
    else:
        macro_f1 = 0.0
        
    return accuracy, macro_precision, macro_recall, macro_f1
