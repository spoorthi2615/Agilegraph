import os
import json
import csv
from datetime import datetime, timezone
from typing import List
from app.experiments.fleiss_kappa.fleiss_result import FleissResult

class FleissReport:
    """
    Exports Fleiss' Kappa statistical artifacts for dissertation reporting.
    """
    @staticmethod
    def generate(results: List[FleissResult], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # CSV Export
        csv_path = os.path.join(output_dir, f"fleiss_report_{timestamp}.csv")
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Number of Assets", "Number of Experts", "Observed Agreement", 
                "Expected Agreement", "Fleiss' Kappa", "Interpretation"
            ])
            for res in results:
                writer.writerow([
                    res.number_of_assets, res.number_of_experts,
                    f"{res.observed_agreement:.4f}",
                    f"{res.expected_agreement:.4f}",
                    f"{res.kappa_score:.4f}",
                    res.interpretation
                ])
                
        # JSON Export
        json_path = os.path.join(output_dir, f"fleiss_report_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)
            
        # Markdown Export
        md_path = os.path.join(output_dir, f"fleiss_report_{timestamp}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Inter-Rater Reliability (Fleiss' Kappa) Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            f.write("| Assets | Experts | Obs. Agree (P̄) | Exp. Agree (P̄e) | Kappa (κ) | Interpretation |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for res in results:
                f.write(f"| {res.number_of_assets} | {res.number_of_experts} | {res.observed_agreement:.4f} | {res.expected_agreement:.4f} | {res.kappa_score:.4f} | **{res.interpretation}** |\n")
