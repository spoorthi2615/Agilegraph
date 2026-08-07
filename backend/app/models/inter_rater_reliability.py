from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class KappaInterpretation(str, Enum):
    """
    Standard interpretation thresholds for Cohen's Kappa score based on Landis and Koch (1977).
    """

    POOR = "POOR"  # Kappa < 0
    SLIGHT = "SLIGHT"  # 0.00 - 0.20
    FAIR = "FAIR"  # 0.21 - 0.40
    MODERATE = "MODERATE"  # 0.41 - 0.60
    SUBSTANTIAL = "SUBSTANTIAL"  # 0.61 - 0.80
    ALMOST_PERFECT = "ALMOST_PERFECT"  # 0.81 - 1.00


class InterRaterReliability(BaseModel):
    """
    Domain model representing the scientific calculation of Fleiss' Kappa
    across multiple cybersecurity experts evaluating a batch of nodes.
    """

    reliability_id: UUID = Field(default_factory=uuid4)

    expert_ids: list[str]
    total_subjects: int

    fleiss_kappa: float
    observed_agreement: float
    expected_agreement: float

    interpretation: KappaInterpretation

    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
