import csv
import json
import os
from datetime import datetime, timezone
from typing import List

from app.experiments.significance.significance_result import SignificanceResult


class SignificanceReport:
    """
    Generates structured tables and data exports containing significance decisions.
    """

    @staticmethod
    def generate(results: List[SignificanceResult], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # CSV Export
        csv_path = os.path.join(output_dir, f"significance_report_{timestamp}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Model A (Ref)",
                    "Model B",
                    "Metric",
                    "Observed Diff",
                    "p-value",
                    "Effect Size",
                    "Alpha",
                    "Decision",
                ]
            )
            for res in results:
                writer.writerow(
                    [
                        res.model_a,
                        res.model_b,
                        res.metric_name,
                        f"{res.observed_difference:.6f}",
                        f"{res.p_value:.6f}",
                        f"{res.effect_size:.4f}",
                        f"{res.alpha:.2f}",
                        res.decision,
                    ]
                )

        # JSON Export
        json_path = os.path.join(output_dir, f"significance_report_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)

        # Markdown Export
        md_path = os.path.join(output_dir, f"significance_report_{timestamp}.md")
        with open(md_path, "w") as f:
            f.write("# Statistical Significance Testing Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            f.write(
                "| Reference Model | Baseline | Metric | Obs. Diff | p-value | Effect Size | Alpha | Decision |\n"
            )
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for res in results:
                f.write(
                    f"| {res.model_a} | {res.model_b} | {res.metric_name} | {res.observed_difference:.6f} | {res.p_value:.6f} | {res.effect_size:.4f} | {res.alpha:.2f} | **{res.decision}** |\n"
                )
