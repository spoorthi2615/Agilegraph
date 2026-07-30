import random
from typing import List
from app.experiments.significance.significance_config import SignificanceConfig
from app.experiments.significance.significance_result import SignificanceResult
from app.experiments.significance.permutation_test import PermutationTest

class SignificanceTestService:
    """
    Orchestrates the statistical significance testing pipeline, pairing metrics and exporting decisions.
    """
    def __init__(self, config: SignificanceConfig):
        self.config = config
        random.seed(self.config.random_seed)
        
    def test_significance(
        self, 
        model_a_name: str, 
        model_b_name: str, 
        metric_name: str, 
        model_a_metrics: List[float], 
        model_b_metrics: List[float]
    ) -> SignificanceResult:
        """
        Executes a paired permutation test comparing Model A against Model B for a specific metric array.
        """
        obs_diff, p_value, effect_size = PermutationTest.execute(
            model_a_metrics, 
            model_b_metrics, 
            self.config.permutations
        )
        
        # Evaluate H0: There is no difference (or A <= B). 
        # Reject H0 if p-value is less than or equal to the significance level alpha.
        decision = "Reject H0" if p_value <= self.config.alpha else "Fail to Reject H0"
        
        return SignificanceResult(
            model_a=model_a_name,
            model_b=model_b_name,
            metric_name=metric_name,
            observed_difference=obs_diff,
            p_value=p_value,
            effect_size=effect_size,
            alpha=self.config.alpha,
            decision=decision
        )
