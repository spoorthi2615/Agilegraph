from pydantic import BaseModel, Field
from typing import Dict, Any

class HeuristicBreakdown(BaseModel):
    """
    Decomposes the total heuristic risk score into its constituent contributing factors.
    """
    asset_id: str
    total_score: float
    
    # Constituent factors (absolute contribution to total score)
    algorithm_strength_penalty: float = 0.0
    certificate_weakness_penalty: float = 0.0
    dependency_risk_penalty: float = 0.0
    exposure_penalty: float = 0.0
    graph_centrality_penalty: float = 0.0
    
    # Metadata
    is_pqc_ready: bool = False
    migration_effort: str = "UNKNOWN"
