import statistics
from datetime import datetime, timezone
from typing import List

from app.models.bootstrap_confidence_interval import BootstrapConfidenceInterval


class BootstrapConfidenceIntervalService:
    """
    Service responsible for rigorously computing statistical confidence intervals
    using the non-parametric percentile bootstrap method with linear interpolation.
    """

    @staticmethod
    def _interpolate_percentile(sorted_values: List[float], percentile: float) -> float:
        """
        Computes the exact value at a given percentile using linear interpolation
        between adjacent array indices.
        """
        n = len(sorted_values)
        if n == 0:
            return 0.0
        if n == 1:
            return sorted_values[0]

        # Calculate continuous array position (0-indexed)
        position = percentile * (n - 1)

        lower_idx = int(position)
        upper_idx = lower_idx + 1

        # Handle exact integer positions or upper boundary limits
        if upper_idx >= n:
            return sorted_values[lower_idx]

        fraction = position - lower_idx

        lower_val = sorted_values[lower_idx]
        upper_val = sorted_values[upper_idx]

        # Calculate linear interpolation
        return lower_val + fraction * (upper_val - lower_val)

    @classmethod
    def calculate_interval(
        cls,
        metric_name: str,
        point_estimate: float,
        bootstrap_values: List[float],
        confidence_level: float = 0.95,
    ) -> BootstrapConfidenceInterval:
        """
        Calculates the exact mathematical lower and upper bounds of a confidence interval
        from an array of bootstrapped metric values utilizing standard Python libraries.
        """

        # 1. Validate inputs
        if not bootstrap_values:
            raise ValueError("Bootstrap values array cannot be empty.")

        if not (0.0 < confidence_level < 1.0):
            raise ValueError(
                f"Confidence level must be strictly between 0.0 and 1.0. Received {confidence_level}."
            )

        num_samples = len(bootstrap_values)
        if num_samples < 2:
            raise ValueError(
                "Bootstrap calculation mathematically requires at least 2 samples to compute standard deviation."
            )

        # 2. Compute Bootstrap Distribution Statistics
        bootstrap_mean = statistics.mean(bootstrap_values)
        bootstrap_std = statistics.stdev(bootstrap_values)

        # 3. Sort values to perform exact percentile extraction
        sorted_values = sorted(bootstrap_values)

        # 4. Calculate Alpha and Percentile Boundaries
        alpha = 1.0 - confidence_level
        lower_percentile = alpha / 2.0
        upper_percentile = 1.0 - (alpha / 2.0)

        # 5. Execute Linear Interpolation for exact bounds
        lower_bound = cls._interpolate_percentile(sorted_values, lower_percentile)
        upper_bound = cls._interpolate_percentile(sorted_values, upper_percentile)

        # 6. Return Immutable Record
        return BootstrapConfidenceInterval(
            metric_name=metric_name,
            point_estimate=point_estimate,
            confidence_level=confidence_level,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            num_bootstrap_samples=num_samples,
            bootstrap_mean=bootstrap_mean,
            bootstrap_std=bootstrap_std,
            calculated_at=datetime.now(timezone.utc),
            metadata={
                "lower_percentile_used": lower_percentile,
                "upper_percentile_used": upper_percentile,
                "interpolation": "linear",
            },
        )
