from pydantic import BaseModel, Field
from typing import List

class SensitivityConfig(BaseModel):
    """
    Defines the parameters for the Sensitivity Analysis Perturbation engine.
    """
    perturbation_scales: List[float] = Field(default=[-0.20, -0.15, -0.10, -0.05, 0.05, 0.10, 0.15, 0.20])
    target_heuristics: List[str] = Field(
        default=["algorithm_strength", "certificate_weakness", "dependency_risk", "exposure", "graph_centrality", "migration_effort"]
    )
