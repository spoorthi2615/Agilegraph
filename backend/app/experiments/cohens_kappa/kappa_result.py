from pydantic import BaseModel
from typing import List

class KappaResult(BaseModel):
    """
    Data model capturing the statistical output of a pairwise inter-rater reliability test.
    """
    rater_a: str
    rater_b: str
    
    observed_agreement: float
    expected_agreement: float
    kappa_score: float
    interpretation: str
    
    # K x K matrix tracking exactly where raters agreed/disagreed
    confusion_matrix: List[List[int]]
