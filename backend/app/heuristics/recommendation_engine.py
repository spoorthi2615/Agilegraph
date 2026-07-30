from pydantic import BaseModel
from typing import List
import logging
from app.heuristics.migration_estimator import RiskReductionMetrics
from app.heuristics.heuristic_breakdown import HeuristicBreakdown

logger = logging.getLogger(__name__)

class MigrationRecommendation(BaseModel):
    asset_id: str
    priority_score: float
    reason: str
    estimated_risk_reduction: RiskReductionMetrics
    migration_effort: str
    suggested_replacement: str
    
class RecommendationEngine:
    """
    Generates prioritized migration recommendations based on heuristic breakdown,
    GNN predictions, and estimated risk reductions.
    """
    def generate_recommendations(
        self, 
        breakdowns: List[HeuristicBreakdown], 
        gnn_predictions: dict  # asset_id -> float (0.0 to 1.0 probability of being high risk)
    ) -> List[MigrationRecommendation]:
        from app.heuristics.migration_estimator import MigrationEstimator
        estimator = MigrationEstimator()
        recommendations = []
        
        for b in breakdowns:
            if b.is_pqc_ready:
                continue # No migration needed
                
            reduction = estimator.estimate_reduction(
                current_total_score=b.total_score,
                algorithm_penalty=b.algorithm_strength_penalty,
                certificate_penalty=b.certificate_weakness_penalty
            )
            
            # Skip if migration doesn't actually reduce risk (e.g. only central, but already strong)
            if reduction.absolute_reduction <= 0.1:
                continue
                
            gnn_risk_modifier = gnn_predictions.get(b.asset_id, 0.5)
            
            # Priority formula: Base reduction * (1 + GNN confidence)
            priority = reduction.absolute_reduction * (1.0 + gnn_risk_modifier)
            
            # Determine replacement heuristic
            replacement = "Kyber-768 / ML-KEM" if "RSA" in b.asset_id or "ECC" in b.asset_id else "AES-256-GCM / SHA-3"
            
            reason = f"Significant risk reduction ({reduction.percentage_reduction:.1f}%) combined with GNN severity prediction."
            
            recommendations.append(MigrationRecommendation(
                asset_id=b.asset_id,
                priority_score=priority,
                reason=reason,
                estimated_risk_reduction=reduction,
                migration_effort=b.migration_effort,
                suggested_replacement=replacement
            ))
            
        # Sort descending by priority_score
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        return recommendations
