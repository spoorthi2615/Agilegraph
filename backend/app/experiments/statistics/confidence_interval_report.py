import csv
import json
import os
from datetime import datetime, timezone
from typing import List

from app.experiments.statistics.confidence_interval_result import (
    ConfidenceIntervalResult,
)


class ConfidenceIntervalReport:
    """
    Exports statistical artifacts into CSV, JSON, and Markdown for dissertation reporting.
    """

    @staticmethod
    def generate(results: List[ConfidenceIntervalResult], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # CSV Export
        csv_path = os.path.join(output_dir, f"ci_report_{timestamp}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Experiment",
                    "Metric",
                    "Mean",
                    "Median",
                    "Std Dev",
                    "Lower Bound",
                    "Upper Bound",
                    "Confidence Level",
                    "Iterations",
                ]
            )
            for res in results:
                for metric_name, ci in res.metrics.items():
                    writer.writerow(
                        [
                            res.experiment_name,
                            metric_name,
                            f"{ci.mean:.4f}",
                            f"{ci.median:.4f}",
                            f"{ci.std_dev:.4f}",
                            f"{ci.lower_bound:.4f}",
                            f"{ci.upper_bound:.4f}",
                            f"{ci.confidence_level:.2f}",
                            ci.bootstrap_iterations,
                        ]
                    )

        # JSON Export
        json_path = os.path.join(output_dir, f"ci_report_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump([r.model_dump() for r in results], f, indent=2)

        # Markdown Export
        md_path = os.path.join(output_dir, f"ci_report_{timestamp}.md")
        with open(md_path, "w") as f:
            f.write("# Statistical Confidence Interval Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            for res in results:
                f.write(f"### Experiment: {res.experiment_name}\n")
                (
                    f.write(
                        f"| Metric | Mean | {res.metrics.get(list(res.metrics.keys())[0]).confidence_level*100:.1f}% Confidence Interval | Std Dev |\n"
                    )
                    if res.metrics
                    else f.write("| Metric | Mean | Confidence Interval | Std Dev |\n")
                )
                f.write("| :--- | :--- | :--- | :--- |\n")
                for metric_name, ci in res.metrics.items():
                    f.write(
                        f"| {metric_name} | {ci.mean:.4f} | {ci.formatted_interval} | {ci.std_dev:.4f} |\n"
                    )
                f.write("\n")
