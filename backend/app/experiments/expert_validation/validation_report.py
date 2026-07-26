import os
import json
import csv
from datetime import datetime, timezone
from app.experiments.expert_validation.validation_dataset import ValidationDataset
from app.experiments.expert_validation.expert_label import RiskLabel

class ValidationReport:
    """
    Generates statistics and structured exports for the expert consensus ground truth dataset.
    """
    @staticmethod
    def generate(dataset: ValidationDataset, experts_count: int, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        total_assets = len(dataset.records)
        disagreements = sum(1 for r in dataset.records if r.disagreement_flag)
        missing_reviews = sum(1 for r in dataset.records if not r.expert_labels)
        
        consensus_counts = {lbl.value: 0 for lbl in RiskLabel}
        for r in dataset.records:
            if r.consensus_label:
                consensus_counts[r.consensus_label.value] += 1
                
        # CSV Export
        csv_path = os.path.join(output_dir, f"validation_dataset_{timestamp}.csv")
        with open(csv_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Asset ID", "Predicted Risk", "Consensus Risk", "Disagreement", "Expert Votes Count"])
            for r in dataset.records:
                writer.writerow([
                    r.asset_id, 
                    r.predicted_risk.value if r.predicted_risk else "", 
                    r.consensus_label.value if r.consensus_label else "", 
                    "Yes" if r.disagreement_flag else "No",
                    len(r.expert_labels)
                ])
                
        # JSON Meta Report
        report_data = {
            "project_id": dataset.project_id,
            "timestamp": timestamp,
            "total_assets": total_assets,
            "experts_participating": experts_count,
            "disagreements": disagreements,
            "missing_reviews": missing_reviews,
            "consensus_distribution": consensus_counts
        }
        
        json_path = os.path.join(output_dir, f"validation_report_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=2)
            
        # Markdown Summary
        md_path = os.path.join(output_dir, f"validation_report_{timestamp}.md")
        with open(md_path, "w") as f:
            f.write("# Expert Validation Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            f.write(f"- **Total Assets:** {total_assets}\n")
            f.write(f"- **Participating Experts:** {experts_count}\n")
            f.write(f"- **Assets with Disagreements:** {disagreements}\n")
            f.write(f"- **Assets with Zero Reviews:** {missing_reviews}\n\n")
            f.write("## Consensus Distribution\n")
            for lbl, count in consensus_counts.items():
                f.write(f"- **{lbl}:** {count}\n")
