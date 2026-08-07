import logging
import math
import random
from typing import Dict, List

from app.experiments.statistics.confidence_interval import ConfidenceInterval
from app.experiments.statistics.confidence_interval_result import ConfidenceIntervalResult
from app.experiments.statistics.statistics_config import StatisticsConfig

logger = logging.getLogger(__name__)


class BootstrapService:
    """
    Computes rigorous non-parametric bootstrap confidence intervals.
    Implemented entirely in native Python to avoid heavy external dependencies
    and mathematically guarantee exact linear interpolated percentiles.
    """

    def __init__(self, config: StatisticsConfig):
        self.config = config
        random.seed(self.config.random_seed)

    def _percentile_linear(self, sorted_data: List[float], p: float) -> float:
        """
        Estimates the exact percentile using linear interpolation between adjacent ranks.
        """
        if not sorted_data:
            return 0.0
        if len(sorted_data) == 1:
            return sorted_data[0]

        i = p * (len(sorted_data) - 1)
        k = int(math.floor(i))
        f = i - k

        if k >= len(sorted_data) - 1:
            return sorted_data[-1]

        return sorted_data[k] * (1.0 - f) + sorted_data[k + 1] * f

    def estimate_confidence_interval(
        self, metric_name: str, data: List[float]
    ) -> ConfidenceInterval:
        """
        Generates B bootstrap samples with replacement, computes the mean of each,
        and extracts the confidence bounds from the resulting sampling distribution.
        """
        if not data:
            raise ValueError(
                f"Cannot compute confidence interval for {metric_name}: data is empty."
            )

        n = len(data)
        bootstrap_means = []

        # Performance: pre-allocate or optimize generator to avoid memory bloat
        for _ in range(self.config.bootstrap_iterations):
            # Sample with replacement
            sample_sum = sum(random.choice(data) for _ in range(n))
            bootstrap_means.append(sample_sum / n)

        # Sort in-place for percentile extraction
        bootstrap_means.sort()

        # Bounds logic
        alpha = 1.0 - self.config.confidence_level
        lower_p = alpha / 2.0
        upper_p = 1.0 - lower_p

        lower_bound = self._percentile_linear(bootstrap_means, lower_p)
        upper_bound = self._percentile_linear(bootstrap_means, upper_p)

        # Central tendencies
        mean_val = sum(bootstrap_means) / len(bootstrap_means)
        median_val = self._percentile_linear(bootstrap_means, 0.5)

        # Standard Deviation of the bootstrap distribution (Standard Error of the mean)
        variance = sum((x - mean_val) ** 2 for x in bootstrap_means) / len(bootstrap_means)
        std_dev = math.sqrt(variance)

        return ConfidenceInterval(
            metric_name=metric_name,
            mean=mean_val,
            median=median_val,
            std_dev=std_dev,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            confidence_level=self.config.confidence_level,
            bootstrap_iterations=self.config.bootstrap_iterations,
        )

    def estimate_experiment_intervals(
        self, experiment_name: str, metrics_data: Dict[str, List[float]]
    ) -> ConfidenceIntervalResult:
        """
        Bulk computes CI for a dictionary of metric arrays.
        """
        results = {}
        for metric_name, data in metrics_data.items():
            results[metric_name] = self.estimate_confidence_interval(metric_name, data)

        return ConfidenceIntervalResult(experiment_name=experiment_name, metrics=results)
