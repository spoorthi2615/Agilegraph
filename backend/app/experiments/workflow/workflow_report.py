import os
import json
from datetime import datetime, timezone
from app.experiments.workflow.workflow_result import WorkflowResult

class WorkflowReport:
    """
    Generates the unified Master Report containing all experiments.
    """
    @staticmethod
    def generate(result: WorkflowResult, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        # JSON Export
        json_path = os.path.join(output_dir, f"workflow_report_{timestamp}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2)
            
        # Markdown Export
        md_path = os.path.join(output_dir, f"workflow_report_{timestamp}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Master Experimental Evaluation Report\n\n")
            f.write(f"**Generated at:** {timestamp} (UTC)\n\n")
            
            f.write("## Execution Durations\n")
            f.write("| Phase | Duration (s) |\n")
            f.write("| :--- | :--- |\n")
            for phase, duration in result.execution_times.items():
                f.write(f"| {phase} | {duration:.4f} |\n")
            f.write("\n")
            
            if result.errors:
                f.write("## Phase Errors\n")
                f.write("> [!WARNING]\n")
                f.write("> The following isolated faults occurred during orchestration:\n\n")
                for phase, err in result.errors.items():
                    f.write(f"- **{phase}**: {err}\n")
                f.write("\n")
                
            if result.benchmark_results:
                f.write("## Benchmark Metrics\n")
                f.write("*(See JSON payload for complete metric breakdown)*\n\n")
                
            if result.ablation_results:
                f.write("## Ablation Study Results\n")
                f.write("*(See JSON payload for complete metric breakdown)*\n\n")
                
            if result.cohens_kappa_results:
                f.write("## Inter-Rater Reliability (Cohen's Kappa)\n")
                f.write("*(See JSON payload for complete matrix breakdown)*\n\n")
                
            if result.fleiss_kappa_results:
                f.write("## Multi-Rater Reliability (Fleiss' Kappa)\n")
                f.write("*(See JSON payload for complete statistical consensus)*\n\n")
