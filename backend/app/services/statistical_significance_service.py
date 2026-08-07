import math
import statistics
from datetime import datetime, timezone
from typing import List

from app.models.significance_test_result import SignificanceTestResult


class StatisticalSignificanceService:
    """
    Service responsible for rigorously computing statistical significance and
    effect sizes between two experimental result sets using only standard libraries.
    """

    @classmethod
    def calculate_significance(
        cls,
        metric_name: str,
        baseline_values: List[float],
        comparison_values: List[float],
        alpha: float = 0.05,
    ) -> SignificanceTestResult:
        """
        Calculates Welch's t-statistic and Cohen's d effect size between a baseline
        and a comparison dataset. Uses the Standard Normal approximation for the p-value
        to remain dependency-free.
        """

        # 1. Validate inputs
        if not baseline_values or not comparison_values:
            raise ValueError("Both baseline and comparison arrays must contain values.")

        n1 = len(baseline_values)
        n2 = len(comparison_values)

        if n1 < 2 or n2 < 2:
            raise ValueError(
                "Variance calculation mathematically requires at least 2 samples in each array."
            )

        if not (0.0 < alpha < 1.0):
            raise ValueError(f"Alpha must be strictly between 0.0 and 1.0. Received {alpha}.")

        # 2. Compute Means and Variances
        mean1 = statistics.mean(baseline_values)
        mean2 = statistics.mean(comparison_values)

        var1 = statistics.variance(baseline_values)
        var2 = statistics.variance(comparison_values)

        mean_diff = mean2 - mean1

        # 3. Calculate Welch's t-statistic (assuming unequal variances)
        # Denominator represents the standard error of the difference
        se_diff = math.sqrt((var1 / n1) + (var2 / n2))

        if se_diff == 0.0:
            # Edge case: If both arrays have zero variance and identical means
            t_stat = 0.0
            p_value = 1.0 if mean1 == mean2 else 0.0
        else:
            t_stat = mean_diff / se_diff

            # 4. Compute p-value using Normal approximation via math.erf
            # For machine learning datasets (N > 30), the t-distribution heavily converges
            # to the standard normal distribution. This provides an extremely precise p-value
            # without requiring the heavy SciPy package to compute incomplete beta functions.
            # Two-tailed p-value = 2 * (1 - CDF(|t|))
            abs_t = abs(t_stat)
            cdf_val = 0.5 * (1.0 + math.erf(abs_t / math.sqrt(2.0)))
            p_value = 2.0 * (1.0 - cdf_val)

        # 5. Compute Cohen's d (Effect Size) using pooled variance
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        if pooled_var > 0:
            effect_size = mean_diff / math.sqrt(pooled_var)
        else:
            effect_size = 0.0

        # 6. Determine Significance against threshold
        is_significant = p_value < alpha

        # Evaluate if the normal approximation was applied to a dangerously small sample
        small_sample_warning = (n1 + n2) < 30

        return SignificanceTestResult(
            metric_name=metric_name,
            baseline_mean=mean1,
            comparison_mean=mean2,
            mean_difference=mean_diff,
            test_name="Welch's t-test (Normal Approximation)",
            test_statistic=t_stat,
            p_value=p_value,
            alpha=alpha,
            statistically_significant=is_significant,
            effect_size=effect_size,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "baseline_n": n1,
                "comparison_n": n2,
                "baseline_variance": var1,
                "comparison_variance": var2,
                "small_sample_warning": small_sample_warning,
            },
        )
