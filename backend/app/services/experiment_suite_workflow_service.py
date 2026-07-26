from typing import List
from datetime import datetime, timezone

from app.models.experiment_execution_report import ExperimentExecutionReport, ExperimentStatus
from app.models.experiment_suite_report import ExperimentSuiteReport


class ExperimentSuiteWorkflowService:
    """
    High-level orchestration service responsible for aggregating multiple AgileGraph 
    experiment executions into a single, comprehensive suite report.
    """

    @classmethod
    def execute_suite(
        cls, 
        suite_name: str,
        suite_description: str,
        experiment_reports: List[ExperimentExecutionReport]
    ) -> ExperimentSuiteReport:
        """
        Validates the experimental artifacts, aggregates the results of multiple 
        experiments, computes overall success statistics, and generates a unified 
        summary without duplicating any underlying benchmark or statistical logic.
        """
        
        # 1. Validate inputs
        if not suite_name or not suite_description:
            raise ValueError("Suite name and suite description must be provided.")
            
        if not experiment_reports:
            raise ValueError("At least one ExperimentExecutionReport is required to execute a suite.")
            
        # 2. Aggregate Experiment Statistics
        total_experiments = len(experiment_reports)
        
        # Count outcomes strictly using the ExperimentStatus Enum
        successful_experiments = sum(
            1 for exp in experiment_reports 
            if exp.overall_result == ExperimentStatus.SUCCESS
        )
        
        tied_experiments = sum(
            1 for exp in experiment_reports 
            if exp.overall_result == ExperimentStatus.STATISTICAL_TIE
        )
        
        failed_experiments = sum(
            1 for exp in experiment_reports 
            if exp.overall_result == ExperimentStatus.FAILURE_BASELINE_RETAINED
        )
        
        # Calculate success rate as a percentage
        success_rate = (successful_experiments / total_experiments) * 100.0
        
        # 3. Generate Summary Narrative
        overall_summary = (
            f"Experiment Suite '{suite_name}' completed {total_experiments} total experiments. "
            f"Achieved {successful_experiments} successes, {tied_experiments} ties, and {failed_experiments} failures, "
            f"resulting in a {success_rate:.2f}% success rate."
        )
        
        # 4. Return Unified Orchestration Payload
        return ExperimentSuiteReport(
            suite_name=suite_name,
            suite_description=suite_description,
            experiment_reports=experiment_reports,
            total_experiments=total_experiments,
            successful_experiments=successful_experiments,
            tied_experiments=tied_experiments,
            failed_experiments=failed_experiments,
            success_rate=success_rate,
            overall_summary=overall_summary,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "perfect_suite": successful_experiments == total_experiments
            }
        )
