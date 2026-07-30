import logging
from app.experiments.fleiss_kappa.fleiss_config import FleissConfig
from app.experiments.fleiss_kappa.fleiss_result import FleissResult
from app.experiments.fleiss_kappa.agreement_matrix import AgreementMatrixEngine
from app.experiments.expert_validation.validation_dataset import ValidationDataset

logger = logging.getLogger(__name__)

class FleissKappaService:
    """
    Computes multi-rater inter-rater reliability using Fleiss' generalized Kappa formula.
    Safely adapts to varying numbers of raters per asset.
    """
    def __init__(self, config: FleissConfig):
        self.config = config
        
    def _interpret_kappa(self, k: float) -> str:
        """
        Landis & Koch (1977) Interpretation Scale for Fleiss' Kappa.
        """
        if k <= 0.00: return "Poor"
        if k <= 0.20: return "Slight"
        if k <= 0.40: return "Fair"
        if k <= 0.60: return "Moderate"
        if k <= 0.80: return "Substantial"
        return "Almost Perfect"
        
    def calculate_kappa(self, dataset: ValidationDataset) -> FleissResult:
        matrix, classes, n_assets, max_experts = AgreementMatrixEngine.build(dataset)
        
        if n_assets == 0:
            raise ValueError("Dataset must contain at least one valid asset with expert labels.")
            
        k = len(classes)
        
        # Calculate the number of raters per subject: n_i
        n_i = [sum(row) for row in matrix]
        
        # Calculate category sums
        cat_sums = [0.0] * k
        for row in matrix:
            for j in range(k):
                cat_sums[j] += row[j]
                
        total_assignments = sum(n_i)
        
        if total_assignments == 0:
            raise ValueError("No expert labels found in the dataset.")
            
        # 1. Calculate Expected Agreement (P_e)
        p_j = [cat_sum / total_assignments for cat_sum in cat_sums]
        p_e = sum(p ** 2 for p in p_j)
        
        # 2. Calculate Observed Agreement (P_bar)
        p_i = []
        for i, row in enumerate(matrix):
            raters_for_item = n_i[i]
            if raters_for_item <= 1:
                # Agreement cannot be mathematically calculated with fewer than 2 raters
                continue
                
            sum_squares = sum(x ** 2 for x in row)
            p_i_val = (sum_squares - raters_for_item) / (raters_for_item * (raters_for_item - 1))
            p_i.append(p_i_val)
            
        if not p_i:
            raise ValueError("No assets have enough expert reviews (requires >= 2 experts per asset) to calculate agreement.")
            
        p_bar = sum(p_i) / len(p_i)
        
        # 3. Calculate Fleiss' Kappa
        if p_e >= 1.0:
            kappa = 1.0 if p_bar == 1.0 else 0.0
        else:
            kappa = (p_bar - p_e) / (1.0 - p_e)
            
        return FleissResult(
            number_of_assets=len(p_i),  # Only count assets that contributed to the agreement metric
            number_of_experts=max_experts,
            observed_agreement=p_bar,
            expected_agreement=p_e,
            kappa_score=kappa,
            interpretation=self._interpret_kappa(kappa),
            agreement_matrix=matrix
        )
