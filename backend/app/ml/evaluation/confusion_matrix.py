import torch


class ConfusionMatrix:
    """
    Mathematically computes the multiclass confusion matrix using pure PyTorch operations.
    Isolated from any ML training logic or external dependencies.
    """

    @staticmethod
    def compute(preds: torch.Tensor, targets: torch.Tensor, num_classes: int) -> dict:
        """
        Returns a dictionary containing the matrix layout, and TP/FP/FN/TN per class.
        """
        matrix = torch.zeros(num_classes, num_classes, dtype=torch.long)

        # Populate matrix: rows are actual targets, cols are predictions
        for t, p in zip(targets.view(-1), preds.view(-1), strict=False):
            matrix[t.long(), p.long()] += 1

        stats = {}
        for c in range(num_classes):
            tp = matrix[c, c].item()
            fn = matrix[c, :].sum().item() - tp
            fp = matrix[:, c].sum().item() - tp
            tn = matrix.sum().item() - tp - fp - fn

            stats[str(c)] = {"TP": tp, "FP": fp, "FN": fn, "TN": tn}

        return {
            "classes": list(range(num_classes)),
            "matrix": matrix.tolist(),
            "stats": stats,
        }
