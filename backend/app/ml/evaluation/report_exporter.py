import os
import csv
from app.ml.evaluation.evaluation_report import EvaluationReport

class ReportExporter:
    """
    Exports the EvaluationReport to JSON, CSV, and Markdown formats.
    """
    def __init__(self, output_dir: str = "backend/outputs/evaluation"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def export_all(self, report: EvaluationReport):
        timestamp = report.evaluation_time.strftime("%Y%m%d_%H%M%S")
        prefix = f"eval_{report.dataset_version}_{timestamp}"
        
        self.export_json(report, os.path.join(self.output_dir, f"{prefix}.json"))
        self.export_csv(report, os.path.join(self.output_dir, f"{prefix}.csv"))
        self.export_markdown(report, os.path.join(self.output_dir, f"{prefix}.md"))
        
    def export_json(self, report: EvaluationReport, path: str):
        with open(path, "w") as f:
            f.write(report.model_dump_json(indent=2))
            
    def export_csv(self, report: EvaluationReport, path: str):
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Class", "Precision", "Recall", "F1", "Support"])
            for cls_id, metrics in report.per_class_metrics.items():
                writer.writerow([cls_id, metrics["precision"], metrics["recall"], metrics["f1"], metrics["support"]])
            writer.writerow(["Macro Avg", report.macro_precision, report.macro_recall, report.macro_f1, ""])
            writer.writerow(["Weighted Avg", report.weighted_precision, report.weighted_recall, report.weighted_f1, ""])
            writer.writerow(["Accuracy", report.overall_accuracy, "", "", ""])
            if report.roc_auc is not None:
                writer.writerow(["ROC-AUC", report.roc_auc, "", "", ""])

    def export_markdown(self, report: EvaluationReport, path: str):
        md = [
            f"# Evaluation Report",
            f"**Model Version:** {report.model_version}",
            f"**Dataset Version:** {report.dataset_version}",
            f"**Time:** {report.evaluation_time}",
            "",
            "## Overall Metrics",
            f"- **Accuracy:** {report.overall_accuracy:.4f}",
            f"- **Macro F1:** {report.macro_f1:.4f}",
            f"- **Weighted F1:** {report.weighted_f1:.4f}",
        ]
        if report.roc_auc is not None:
            md.append(f"- **ROC-AUC:** {report.roc_auc:.4f}")
            
        md.append("")
        md.append("## Per-Class Metrics")
        md.append("| Class | Precision | Recall | F1-Score | Support |")
        md.append("|---|---|---|---|---|")
        for c, m in report.per_class_metrics.items():
            md.append(f"| {c} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1']:.4f} | {m['support']} |")
            
        with open(path, "w") as f:
            f.write("\n".join(md))
