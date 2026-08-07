from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.explanation import Explanation
from app.models.migration_recommendation import MigrationRecommendation
from app.models.pqc_readiness import PQCReadinessLevel


class SecurityReport(BaseModel):
    """
    Domain model representing a comprehensive, consolidated security assessment
    and Post-Quantum Cryptography roadmap for an entire project codebase.
    """

    report_id: UUID = Field(default_factory=uuid4)
    project_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_assets: int
    total_high_risk_assets: int
    pqc_readiness_score: float
    pqc_readiness_level: PQCReadinessLevel
    total_recommendations: int
    total_cves: int = 0
    mosca_status: str = "Unknown"
    roadmap_summary: str
    executive_summary: str
    recommendations: List[MigrationRecommendation]
    explanations: List[Explanation]
