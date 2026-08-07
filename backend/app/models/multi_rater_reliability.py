from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.inter_rater_reliability import KappaInterpretation


class MultiRaterReliability(BaseModel):
    """
    Domain model representing the scientific calculation of Fleiss' Kappa
    for three or more cybersecurity experts assessing a single graph node.
    """

    reliability_id: UUID = Field(default_factory=uuid4)
    node_id: str

    expert_ids: List[str]
    total_experts: int

    fleiss_kappa: float
    observed_agreement: float
    expected_agreement: float

    interpretation: KappaInterpretation

    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
