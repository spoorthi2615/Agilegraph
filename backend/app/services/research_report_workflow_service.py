from typing import List
from datetime import datetime, timezone

from app.models.experiment_suite_report import ExperimentSuiteReport
from app.models.research_report import ResearchReport


class ResearchReportWorkflowService:
    """
    High-level orchestration service responsible for wrapping a massive Experiment Suite 
    into a final, publication-ready research report with executive summaries and findings.
    """

    @classmethod
    def generate_research_report(
        cls, 
        report_title: str,
        report_description: str,
        experiment_suite_report: ExperimentSuiteReport,
        production_readiness_threshold: float = 75.0
    ) -> ResearchReport:
        """
        Validates the experimental suite artifact, generates human-readable executive summaries, 
        extracts key findings across all experiments, and provides structural recommendations 
        based on configurable business thresholds.
        """
        
        # 1. Validate inputs
        if not report_title or not report_description:
            raise ValueError("Report title and description must be provided.")
            
        if not experiment_suite_report:
            raise ValueError("An ExperimentSuiteReport is strictly required to generate a ResearchReport.")
            
        if not (0.0 <= production_readiness_threshold <= 100.0):
            raise ValueError("Production readiness threshold must be a percentage between 0.0 and 100.0.")
            
        # 2. Extract Data for Generation
        success_rate = experiment_suite_report.success_rate
        total_exp = experiment_suite_report.total_experiments
        successful_exp = experiment_suite_report.successful_experiments
        tied_exp = experiment_suite_report.tied_experiments
        
        # 3. Generate Executive Summary
        executive_summary = (
            f"This research report, '{report_title}', encompasses {total_exp} highly controlled experiments. "
            f"The experimental architecture achieved a decisive success rate of {success_rate:.2f}%. "
            f"Specifically, {successful_exp} experiments demonstrated statistically significant improvements, "
            f"and {tied_exp} experiments matched baseline performance."
        )
        
        # 4. Extract Key Findings
        key_findings: List[str] = []
        
        if success_rate >= 90.0:
            key_findings.append("The experimental architecture demonstrates overwhelmingly superior performance across the evaluation corpus.")
        elif success_rate >= 50.0:
            key_findings.append("The experimental architecture shows promising improvements in a majority of tested scenarios.")
        else:
            key_findings.append("The experimental architecture fails to consistently outperform the established baseline.")
            
        # Search for critical components across all nested ablation reports
        critical_components = set()
        for exp in experiment_suite_report.experiment_reports:
            for ab in exp.ablation_reports:
                if "CRITICAL" in ab.component_importance:
                    critical_components.add(ab.component_name)
                    
        if critical_components:
            components_str = ", ".join(sorted(list(critical_components)))
            key_findings.append(f"Ablation studies confirmed the absolute criticality of the following components: {components_str}.")
            
        # 5. Generate Recommendations using configurable business thresholds
        recommendations: List[str] = []
        
        is_production_ready = success_rate >= production_readiness_threshold
        
        if is_production_ready:
            recommendations.append(f"The experimental architecture achieved a success rate of {success_rate:.2f}%, exceeding the required threshold of {production_readiness_threshold:.2f}%. It is mathematically sound and recommended for production deployment.")
        else:
            recommendations.append(f"Do not deploy. The success rate of {success_rate:.2f}% failed to meet the required threshold of {production_readiness_threshold:.2f}%. Further architectural refinement is required.")
            
        if critical_components:
            recommendations.append("Ensure robust unit testing is applied to all identified critical components to prevent regression.")
            
        # 6. Return Unified Orchestration Payload
        return ResearchReport(
            report_title=report_title,
            report_description=report_description,
            experiment_suite_report=experiment_suite_report,
            executive_summary=executive_summary,
            key_findings=key_findings,
            recommendations=recommendations,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "is_production_ready": is_production_ready,
                "production_readiness_threshold_used": production_readiness_threshold,
                "critical_components_count": len(critical_components)
            }
        )
