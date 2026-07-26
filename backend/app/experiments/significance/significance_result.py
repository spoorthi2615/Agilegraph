from pydantic import BaseModel

class SignificanceResult(BaseModel):
    """
    Data model capturing the statistical output of a Paired Permutation test comparison.
    """
    model_a: str  # Reference Model (AgileGraph)
    model_b: str  # Baseline Model
    metric_name: str
    
    observed_difference: float
    p_value: float
    effect_size: float
    alpha: float
    
    decision: str  # "Reject H0" or "Fail to Reject H0"
