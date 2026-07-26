import logging
from typing import List
from app.experiments.cohens_kappa.kappa_config import KappaConfig
from app.experiments.cohens_kappa.kappa_result import KappaResult
from app.experiments.cohens_kappa.confusion_matrix import ConfusionMatrixEngine

logger = logging.getLogger(__name__)

class CohensKappaService:
    """
    Computes inter-rater reliability accounting for chance agreement using pure native python logic.
    """
    def __init__(self, config: KappaConfig):
        self.config = config
        
    def _interpret_kappa(self, k: float) -> str:
        """
        Landis & Koch (1977) Interpretation Scale for Cohen's Kappa.
        """
        if k <= 0.00: return "Poor"
        if k <= 0.20: return "Slight"
        if k <= 0.40: return "Fair"
        if k <= 0.60: return "Moderate"
        if k <= 0.80: return "Substantial"
        return "Almost Perfect"
        
    def calculate_kappa(self, rater_a_name: str, rater_b_name: str, labels_a: List[str], labels_b: List[str]) -> KappaResult:
        if not labels_a or not labels_b or len(labels_a) != len(labels_b):
            raise ValueError("Label arrays must be non-empty and of equal length.")
            
        matrix, classes = ConfusionMatrixEngine.build(labels_a, labels_b)
        n = len(classes)
        total = len(labels_a)
        
        # 1. Calculate Observed Agreement (Po)
        observed_agree_count = sum(matrix[i][i] for i in range(n))
        p_o = observed_agree_count / total if total > 0 else 0.0
        
        # 2. Calculate Expected Agreement (Pe)
        p_e = 0.0
        for i in range(n):
            marginal_a = sum(matrix[i][j] for j in range(n))
            marginal_b = sum(matrix[j][i] for j in range(n))
            p_e += (marginal_a * marginal_b) / (total * total) if total > 0 else 0.0
            
        # 3. Calculate Cohen's Kappa
        # Safe edge case bounding for single-class datasets (where Pe == 1.0)
        if p_e >= 1.0:
            kappa = 1.0 if p_o == 1.0 else 0.0
        else:
            kappa = (p_o - p_e) / (1.0 - p_e)
            
        return KappaResult(
            rater_a=rater_a_name,
            rater_b=rater_b_name,
            observed_agreement=p_o,
            expected_agreement=p_e,
            kappa_score=kappa,
            interpretation=self._interpret_kappa(kappa),
            confusion_matrix=matrix
        )
