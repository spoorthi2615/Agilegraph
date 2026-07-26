from pydantic import BaseModel, Field

class StatisticsConfig(BaseModel):
    """
    Configuration for non-parametric bootstrap sampling and confidence interval estimation.
    """
    bootstrap_iterations: int = Field(default=1000, ge=1)
    confidence_level: float = Field(default=0.95, gt=0.0, lt=1.0)
    random_seed: int = Field(default=42)
    output_directory: str = Field(default="outputs/statistics")
