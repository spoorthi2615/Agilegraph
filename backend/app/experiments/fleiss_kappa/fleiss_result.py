from typing import List

from pydantic import BaseModel


class FleissResult(BaseModel):
    """
    Data model capturing the statistical output of a multi-rater Fleiss' Kappa test.
    """

    number_of_assets: int
    number_of_experts: int

    observed_agreement: float
    expected_agreement: float
    kappa_score: float
    interpretation: str

    # N x k matrix representing the distribution of votes per asset per category
    agreement_matrix: List[List[int]]
