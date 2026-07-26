from datetime import datetime, timezone

from app.models.benchmark_report import BenchmarkReport
from app.models.ablation_study_report import AblationStudyReport

class AblationStudyWorkflowService:
    """
    Orchestration service responsible for aggregating an ablation study by evaluating 
    the performance degradation caused by removing a specific architectural component.
    """

    @classmethod
    def generate_ablation_report(
        cls, 
        experiment_name: str,
        component_name: str,
        benchmark_report: BenchmarkReport,
        is_higher_better: bool = True
    ) -> AblationStudyReport:
        """
        Computes the absolute and relative performance drop resulting from the ablation 
        of a component, classifies its structural importance, and securely wraps the provided 
        statistical proofs (BenchmarkReport) into a final unified payload.
        """
        
        # 1. Validate inputs
        if not experiment_name or not component_name:
            raise ValueError("Experiment and component names must be provided.")
            
        # 2. Extract authoritative metrics from the BenchmarkReport
        baseline_metric = benchmark_report.baseline_value
        ablated_metric = benchmark_report.comparison_value
            
        # 3. Compute Performance Drop
        # If higher is better (e.g., Accuracy), removing a critical component causes 
        # the metric to go down. The absolute drop is baseline - ablated.
        # If lower is better (e.g., Loss), removing a critical component causes 
        # the metric to go UP. The absolute drop is ablated - baseline.
        if is_higher_better:
            performance_drop = baseline_metric - ablated_metric
        else:
            performance_drop = ablated_metric - baseline_metric
            
        # Protect against division by zero if the baseline happens to be exactly 0.0
        if baseline_metric == 0.0:
            relative_drop = 0.0
        else:
            relative_drop = (performance_drop / abs(baseline_metric)) * 100.0
            
        # 4. Determine Component Importance based on mathematical variance
        # A component is "CRITICAL" if its removal significantly degrades performance.
        # It is "MARGINAL" if performance drops, but the drop is mathematically noisy (not significant).
        # It is "REDUNDANT" (or detrimental) if removing it actually improves performance or does nothing.
        
        is_significant = False
        if benchmark_report.significance_test:
            is_significant = benchmark_report.significance_test.statistically_significant
            
        if performance_drop > 0.0 and is_significant:
            component_importance = "CRITICAL"
        elif performance_drop > 0.0 and not is_significant:
            component_importance = "MARGINAL"
        elif performance_drop <= 0.0 and is_significant:
            component_importance = "DETRIMENTAL (Removal Mathematically Improves System)"
        else:
            component_importance = "REDUNDANT (No Significant Impact)"
            
        # 5. Generate Summary Narrative
        summary = (
            f"Ablation Study '{experiment_name}' evaluated the removal of component '{component_name}'. "
            f"Performance changed from {baseline_metric:.4f} to {ablated_metric:.4f}. "
            f"This resulted in a relative drop of {relative_drop:.2f}%. "
            f"The component is classified as: {component_importance}."
        )
        
        # 6. Return Unified Orchestration Payload
        return AblationStudyReport(
            experiment_name=experiment_name,
            component_name=component_name,
            baseline_metric=baseline_metric,
            ablated_metric=ablated_metric,
            performance_drop=performance_drop,
            relative_drop=relative_drop,
            component_importance=component_importance,
            benchmark_report=benchmark_report,
            summary=summary,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "zero_baseline_division_avoided": baseline_metric == 0.0,
                "is_higher_better": is_higher_better
            }
        )
