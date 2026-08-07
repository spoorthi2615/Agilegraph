import csv
import json
import os
from datetime import datetime, timezone
from typing import List

from app.experiments.cohens_kappa.kappa_result import KappaResult


class KappaReport:
    """
    Exports statistical artifacts into CSV, JSON, and Markdown for dissertation reporting.
    """

    @staticmethod
    def generate(results: List[KappaResult], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # CSV Export
        csv_path = os.path.join(output_dir, f"kappa_report_{timestamp}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Rater A",
                    "Rater B",
                    "Observed Agreement",
                    "Expected Agreement",
                    "Cohen's Kappa",
                    "Interpretation",
                ]
            )
            for res in results:
                writer.writerow(
                    [
                        res.rater_a,
                        res.rater_b,
                        f"{res.observed_agreement:.4f}",
                        f"{res.expected_agreement:.4f}",
                        f"{res.kappa_score:.4f}",
                        res.interpretation,
                    ]
                )

        # JSON Export
        json_path = os.path.join(output_dir, f"kappa_report_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)

        # Markdown Export
        md_path = os.path.join(output_dir, f"kappa_report_{timestamp}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Inter-Rater Reliability (Cohen's Kappa) Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            f.write(
                "| Rater A | Rater B | Obs. Agree (Po) | Exp. Agree (Pe) | Kappa (κ) | Interpretation |\n"
            )
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for res in results:
                f.write(
                    f"| {res.rater_a} | {res.rater_b} | {res.observed_agreement:.4f} | {res.expected_agreement:.4f} | {res.kappa_score:.4f} | **{res.interpretation}** |\n"
                )
