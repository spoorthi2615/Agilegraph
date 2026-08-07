from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PQCReadinessLevel(str, Enum):
    READY = "READY"
    MOSTLY_READY = "MOSTLY_READY"
    PARTIALLY_READY = "PARTIALLY_READY"
    NOT_READY = "NOT_READY"


class PQCReadinessAssessment(BaseModel):
    """
    Domain model representing the Post-Quantum Cryptography readiness state of an entire project graph.
    """

    assessment_id: UUID = Field(default_factory=uuid4)
    overall_score: float
    readiness_level: PQCReadinessLevel
    total_crypto_assets: int
    pqc_ready_assets: int
    classical_assets: int
    migration_candidates: int
    summary: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
