from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class RiskReductionMetrics(BaseModel):
    current_risk: float
    projected_risk: float
    absolute_reduction: float
    percentage_reduction: float

class MigrationEstimator:
    """
    Estimates the reduction in organizational risk if a vulnerable asset is migrated to a PQC-ready equivalent.
    """
    def estimate_reduction(self, current_total_score: float, algorithm_penalty: float, certificate_penalty: float) -> RiskReductionMetrics:
        """
        Calculates projected risk by assuming the algorithm and certificate penalties are driven to 0 
        (post-migration to strong algorithms and certs). Exposure and Graph Centrality penalties remain,
        as the asset occupies the same structural position.
        """
        # Projected risk removes the algorithm and cert penalties
        reduction = algorithm_penalty + certificate_penalty
        projected = max(0.0, current_total_score - reduction)
        
        absolute_reduction = current_total_score - projected
        percentage_reduction = (absolute_reduction / current_total_score) * 100.0 if current_total_score > 0 else 0.0
        
        return RiskReductionMetrics(
            current_risk=current_total_score,
            projected_risk=projected,
            absolute_reduction=absolute_reduction,
            percentage_reduction=percentage_reduction
        )
