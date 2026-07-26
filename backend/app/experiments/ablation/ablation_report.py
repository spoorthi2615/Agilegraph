import os
import json
import csv
from datetime import datetime, timezone
from typing import List
from app.experiments.ablation.ablation_result import AblationResult

class AblationReport:
    @staticmethod
    def generate(results: List[AblationResult], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # CSV
        csv_path = os.path.join(output_dir, f"ablation_report_{timestamp}.csv")
        with open(csv_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Experiment (Disabled Component)", "Accuracy", "Macro F1", "Weighted F1",
                "Accuracy Drop", "Macro F1 Drop", "Performance Drop %", "Execution Time (ms)"
            ])
            for r in results:
                writer.writerow([
                    r.experiment_name, f"{r.accuracy:.4f}", f"{r.macro_f1:.4f}", f"{r.weighted_f1:.4f}",
                    f"{r.accuracy_drop:.4f}", f"{r.macro_f1_drop:.4f}", f"{r.percentage_performance_drop:.2f}%",
                    f"{r.execution_time_ms:.2f}"
                ])
                
        # JSON
        json_path = os.path.join(output_dir, f"ablation_report_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)
            
        # Markdown
        md_path = os.path.join(output_dir, f"ablation_report_{timestamp}.md")
        with open(md_path, "w") as f:
            f.write("# AgileGraph Ablation Study Report\n\n")
            f.write(f"Generated at: {timestamp} (UTC)\n\n")
            f.write("| Experiment | Accuracy | Macro F1 | Weighted F1 | Performance Drop % | Exec Time (ms) |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for r in results:
                f.write(f"| {r.experiment_name} | {r.accuracy:.4f} | {r.macro_f1:.4f} | {r.weighted_f1:.4f} | {r.percentage_performance_drop:.2f}% | {r.execution_time_ms:.2f} |\n")
