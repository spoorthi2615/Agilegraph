import logging
from typing import Dict, Any
from app.heuristics.heuristic_breakdown import HeuristicBreakdown

logger = logging.getLogger(__name__)

class HeuristicExplainer:
    """
    Interprets raw heuristic scoring payloads and generates a clean,
    mathematically sound decomposition (HeuristicBreakdown) of the risk score.
    Does NOT duplicate heuristic calculation logic; merely exposes it.
    """
    def decompose_score(self, asset_id: str, raw_scoring_payload: Dict[str, Any]) -> HeuristicBreakdown:
        """
        Extracts the fractional components from the raw scoring output.
        """
        try:
            total_score = float(raw_scoring_payload.get("total_score", 0.0))
            factors = raw_scoring_payload.get("factors", {})
            
            return HeuristicBreakdown(
                asset_id=asset_id,
                total_score=total_score,
                algorithm_strength_penalty=float(factors.get("algorithm_strength", 0.0)),
                certificate_weakness_penalty=float(factors.get("certificate_weakness", 0.0)),
                dependency_risk_penalty=float(factors.get("dependency_risk", 0.0)),
                exposure_penalty=float(factors.get("exposure", 0.0)),
                graph_centrality_penalty=float(factors.get("graph_centrality", 0.0)),
                is_pqc_ready=bool(raw_scoring_payload.get("is_pqc_ready", False)),
                migration_effort=str(raw_scoring_payload.get("migration_effort", "UNKNOWN"))
            )
        except Exception as e:
            logger.error(f"Failed to decompose heuristic score for asset '{asset_id}': {e}")
            return HeuristicBreakdown(asset_id=asset_id, total_score=0.0)
