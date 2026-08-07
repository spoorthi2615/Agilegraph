from datetime import datetime, timezone
from typing import Optional

from app.models.benchmark_report import BenchmarkReport
from app.models.bootstrap_confidence_interval import BootstrapConfidenceInterval
from app.models.significance_test_result import SignificanceTestResult


class BaselineBenchmarkWorkflowService:
    """
    Orchestration service responsible for aggregating raw evaluation metrics,
    confidence intervals, and significance tests into a unified benchmark report.
    """

    @classmethod
    def generate_benchmark_report(
        cls,
        metric_name: str,
        baseline_name: str,
        comparison_name: str,
        baseline_value: float,
        comparison_value: float,
        confidence_interval: Optional[BootstrapConfidenceInterval] = None,
        significance_test: Optional[SignificanceTestResult] = None,
        is_higher_better: bool = True,
    ) -> BenchmarkReport:
        """
        Computes absolute and relative improvement between two approaches, attaches
        pre-computed statistical rigor, and decisively declares a winner without
        duplicating statistical logic. Adapts seamlessly to both performance metrics
        and error loss metrics.
        """

        # 1. Validate inputs
        if not baseline_name or not comparison_name:
            raise ValueError("Baseline and comparison names must be provided.")

        # 2. Compute Improvement Metrics
        # By default, a positive delta means the comparison value is mathematically larger.
        raw_delta = comparison_value - baseline_value

        # We define 'improvement' as a positive number when the comparison model is "better".
        if is_higher_better:
            improvement = raw_delta
        else:
            # If lower is better (e.g., Loss metrics), a lower comparison value is an improvement.
            # Inverting the delta ensures that a positive 'improvement' still indicates success.
            improvement = -raw_delta

        # Protect against division by zero if the baseline happens to be exactly 0.0
        if baseline_value == 0.0:
            relative_improvement = 0.0
        else:
            relative_improvement = (improvement / abs(baseline_value)) * 100.0

        # 3. Determine the Winner
        # An approach is only declared the definitive winner if it is mathematically
        # superior AND statistically significant. If the difference is just noise,
        # the system conservatively defaults to the baseline.

        is_significant = True
        if significance_test is not None:
            is_significant = significance_test.statistically_significant

        if improvement > 0.0 and is_significant:
            winner = comparison_name
        elif improvement < 0.0 and is_significant:
            winner = baseline_name
        else:
            winner = f"TIE (Default: {baseline_name})"

        # 4. Return Unified Orchestration Payload
        return BenchmarkReport(
            metric_name=metric_name,
            baseline_name=baseline_name,
            comparison_name=comparison_name,
            baseline_value=baseline_value,
            comparison_value=comparison_value,
            improvement=improvement,
            relative_improvement=relative_improvement,
            confidence_interval=confidence_interval,
            significance_test=significance_test,
            winner=winner,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "zero_baseline_division_avoided": baseline_value == 0.0,
                "is_higher_better": is_higher_better,
            },
        )
