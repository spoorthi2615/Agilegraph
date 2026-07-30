import os
import json
import csv
from typing import List
from app.benchmark.benchmark_result import BenchmarkResult
from app.benchmark.benchmark_config import BenchmarkConfig

class BenchmarkReport:
    """
    Handles the serialization of BenchmarkResult arrays into JSON, CSV, and Markdown logs.
    Strictly outputs raw predictions without computing statistical evaluations.
    """
    def __init__(self, config: BenchmarkConfig):
        self.output_dir = config.output_directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self, results: List[BenchmarkResult]) -> None:
        if not results:
            return
            
        timestamp = results[0].timestamp.strftime("%Y%m%d_%H%M%S")
        project_id = results[0].project_id
        
        prefix = f"benchmark_{project_id}_{timestamp}"
        
        self._generate_json(results, os.path.join(self.output_dir, f"{prefix}.json"))
        self._generate_csv(results, os.path.join(self.output_dir, f"{prefix}.csv"))
        self._generate_markdown(results, os.path.join(self.output_dir, f"{prefix}.md"))
        
    def _generate_json(self, results: List[BenchmarkResult], path: str) -> None:
        data = [res.model_dump() for res in results]
        # Pydantic UUID and datetime serialization workaround
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
            
    def _generate_csv(self, results: List[BenchmarkResult], path: str) -> None:
        with open(path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Baseline Name", "Model Version", "Execution Time (ms)", "Prediction Count", "Timestamp"])
            for res in results:
                writer.writerow([
                    res.baseline_name, 
                    res.model_version, 
                    f"{res.execution_time_ms:.2f}",
                    res.prediction_count,
                    res.timestamp.isoformat()
                ])
                
    def _generate_markdown(self, results: List[BenchmarkResult], path: str) -> None:
        md = [
            "# Benchmark Execution Report",
            f"**Project ID:** {results[0].project_id}",
            f"**Execution Time:** {results[0].timestamp}",
            "",
            "## Performance Summary",
            "| Baseline Name | Execution Latency (ms) | Predictions Generated | Model Version |",
            "|---|---|---|---|"
        ]
        
        for res in results:
            md.append(f"| {res.baseline_name} | {res.execution_time_ms:.2f} | {res.prediction_count} | {res.model_version} |")
            
        md.append("")
        md.append("> Raw predictions are exported to the companion CSV and JSON files for formal statistical computation in Sprint 62.")
        
        with open(path, "w") as f:
            f.write("\n".join(md))
