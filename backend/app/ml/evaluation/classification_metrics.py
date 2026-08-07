import torch


class ClassificationMetrics:
    """
    Computes Precision, Recall, F1, and Accuracy for multiclass scenarios.
    Supports per-class extraction, Macro-averaging, and Weighted-averaging.
    """

    @staticmethod
    def compute(preds: torch.Tensor, targets: torch.Tensor, num_classes: int) -> dict:
        correct = (preds == targets).sum().item()
        total = targets.size(0)

        overall_accuracy = correct / total if total > 0 else 0.0

        per_class = {}
        total_support = 0

        for c in range(num_classes):
            tp = ((preds == c) & (targets == c)).sum().item()
            fp = ((preds == c) & (targets != c)).sum().item()
            fn = ((preds != c) & (targets == c)).sum().item()
            support = (targets == c).sum().item()

            total_support += support

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            )

            per_class[str(c)] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": support,
            }

        # Macro averages
        macro_p = sum(c_metrics["precision"] for c_metrics in per_class.values()) / num_classes
        macro_r = sum(c_metrics["recall"] for c_metrics in per_class.values()) / num_classes
        macro_f1 = sum(c_metrics["f1"] for c_metrics in per_class.values()) / num_classes

        # Weighted averages
        if total_support > 0:
            weighted_p = (
                sum(c["precision"] * c["support"] for c in per_class.values()) / total_support
            )
            weighted_r = sum(c["recall"] * c["support"] for c in per_class.values()) / total_support
            weighted_f1 = sum(c["f1"] * c["support"] for c in per_class.values()) / total_support
        else:
            weighted_p, weighted_r, weighted_f1 = 0.0, 0.0, 0.0

        return {
            "overall_accuracy": overall_accuracy,
            "macro_precision": macro_p,
            "macro_recall": macro_r,
            "macro_f1": macro_f1,
            "weighted_precision": weighted_p,
            "weighted_recall": weighted_r,
            "weighted_f1": weighted_f1,
            "per_class": per_class,
        }
