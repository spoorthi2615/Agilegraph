from pydantic import BaseModel


class ConfidenceInterval(BaseModel):
    """
    A mathematical representation of a metric's distribution and uncertainty.
    """

    metric_name: str

    mean: float
    median: float
    std_dev: float

    lower_bound: float
    upper_bound: float

    confidence_level: float
    bootstrap_iterations: int

    @property
    def formatted_interval(self) -> str:
        return (
            f"{self.confidence_level*100:.1f}% CI: [{self.lower_bound:.4f}, {self.upper_bound:.4f}]"
        )
