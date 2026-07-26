import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import logging

from app.ml.evaluation.evaluation_report import EvaluationReport
from app.ml.evaluation.confusion_matrix import ConfusionMatrix
from app.ml.evaluation.classification_metrics import ClassificationMetrics
from app.ml.evaluation.roc_metrics import ROCMetrics
from app.ml.evaluation.report_exporter import ReportExporter

class GATv2Evaluator:
    """
    Core orchestrator for GATv2 evaluation.
    Strictly isolated from training logic.
    """
    def __init__(self, model: torch.nn.Module, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.exporter = ReportExporter()
        
    def load_checkpoint(self, path: str):
        """Loads weights safely via weights_only=True."""
        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=True)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logging.info(f"Loaded checkpoint from {path}")
        except Exception as e:
            logging.error(f"Failed to load checkpoint at {path}: {str(e)}")
            raise
        
    def evaluate(self, data: Data, dataset_version: str = "latest", num_classes: int = 4) -> EvaluationReport:
        """
        Executes inference, evaluates predictions, and compiles the EvaluationReport.
        """
        data = data.to(self.device)
        
        # Enforce evaluation mode
        self.model.eval()
        
        # Disable gradients to prevent memory leaks and ensure pure inference
        with torch.no_grad():
            logits = self.model(data)
            probs = F.softmax(logits, dim=1)
            preds = logits.argmax(dim=1)
            
        # Filter unlabeled nodes (-1)
        mask = data.y != -1
        filtered_preds = preds[mask]
        filtered_targets = data.y[mask]
        filtered_probs = probs[mask]
        
        if len(filtered_targets) == 0:
            logging.warning("No labeled data found for evaluation.")
            return EvaluationReport(dataset_version=dataset_version)
            
        # Compute Statistical Metrics
        cls_metrics = ClassificationMetrics.compute(filtered_preds, filtered_targets, num_classes)
        conf_matrix = ConfusionMatrix.compute(filtered_preds, filtered_targets, num_classes)
        roc_auc = ROCMetrics.compute(filtered_probs, filtered_targets, num_classes)
        
        report = EvaluationReport(
            dataset_version=dataset_version,
            overall_accuracy=cls_metrics["overall_accuracy"],
            macro_precision=cls_metrics["macro_precision"],
            macro_recall=cls_metrics["macro_recall"],
            macro_f1=cls_metrics["macro_f1"],
            weighted_precision=cls_metrics["weighted_precision"],
            weighted_recall=cls_metrics["weighted_recall"],
            weighted_f1=cls_metrics["weighted_f1"],
            per_class_metrics=cls_metrics["per_class"],
            confusion_matrix=conf_matrix,
            roc_auc=roc_auc
        )
        
        self.exporter.export_all(report)
        return report
