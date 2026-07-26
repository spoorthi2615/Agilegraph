from pydantic import BaseModel, Field

class SignificanceConfig(BaseModel):
    """
    Configuration parameters for non-parametric paired permutation tests.
    """
    permutations: int = Field(default=10000, ge=1)
    alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    random_seed: int = Field(default=42)
    output_directory: str = Field(default="outputs/significance")
