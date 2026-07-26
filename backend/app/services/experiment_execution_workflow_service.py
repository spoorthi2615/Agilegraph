from typing import List
from datetime import datetime, timezone

from app.models.benchmark_report import BenchmarkReport
from app.models.ablation_study_report import AblationStudyReport
from app.models.experiment_execution_report import ExperimentExecutionReport, ExperimentStatus

class ExperimentExecutionWorkflowService:
    """
    High-level orchestration service responsible for wrapping a complete AgileGraph 
    experiment (benchmarks and ablation studies) into a single, cohesive narrative.
    """

    @classmethod
    def execute_experiment(
        cls, 
        experiment_name: str,
        experiment_description: str,
        benchmark_report: BenchmarkReport,
        ablation_reports: List[AblationStudyReport]
    ) -> ExperimentExecutionReport:
        """
        Validates the experimental artifacts, determines the overall success of the 
        experiment using strictly typed Enums, and generates a unified summary 
        without duplicating any underlying mathematical or benchmark logic.
        """
        
        # 1. Validate inputs
        if not experiment_name or not experiment_description:
            raise ValueError("Experiment name and experiment description must be provided.")
            
        if not benchmark_report:
            raise ValueError("A BenchmarkReport is strictly required to execute an experiment.")
            
        if ablation_reports is None:
            ablation_reports = []
            
        # 2. Determine Overall Result using strictly typed Enums
        comparison_name = benchmark_report.comparison_name
        baseline_name = benchmark_report.baseline_name
        winner = benchmark_report.winner
        
        if winner == comparison_name:
            overall_result = ExperimentStatus.SUCCESS
        elif winner == baseline_name:
            overall_result = ExperimentStatus.FAILURE_BASELINE_RETAINED
        else:
            overall_result = ExperimentStatus.STATISTICAL_TIE
        
        # 3. Generate Summary Narrative
        num_ablations = len(ablation_reports)
        critical_components = [
            ab.component_name 
            for ab in ablation_reports 
            if "CRITICAL" in ab.component_importance
        ]
        
        summary = (
            f"Experiment '{experiment_name}' completed with status: {overall_result.value}. "
            f"Compared {comparison_name} against {baseline_name}. "
            f"Included {num_ablations} ablation studies. "
        )
        
        if critical_components:
            summary += f"Identified critical components: {', '.join(critical_components)}."
            
        # 4. Return Unified Orchestration Payload
        return ExperimentExecutionReport(
            experiment_name=experiment_name,
            experiment_description=experiment_description,
            benchmark_report=benchmark_report,
            ablation_reports=ablation_reports,
            overall_result=overall_result,
            summary=summary,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "is_success": overall_result == ExperimentStatus.SUCCESS,
                "total_ablations": num_ablations
            }
        )
