from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.inter_rater_reliability import InterRaterReliability
from app.models.multi_rater_reliability import MultiRaterReliability


class StatisticalValidationReport(BaseModel):
    """
    Domain model representing the macroscopic, repository-wide statistical analysis
    of expert inter-rater reliability across the entire codebase.
    """

    report_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    total_nodes_validated: int
    total_expert_validations: int

    pairwise_reliability_results: List[InterRaterReliability]
    multi_rater_reliability_results: List[MultiRaterReliability]

    average_cohens_kappa: float
    average_fleiss_kappa: float

    high_reliability_nodes: List[str]
    low_reliability_nodes: List[str]

    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
