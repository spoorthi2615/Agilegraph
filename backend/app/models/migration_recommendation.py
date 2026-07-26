from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum
from app.models.crypto_asset import Severity

class Priority(str, Enum):
    IMMEDIATE = "Immediate"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class MigrationRecommendation(BaseModel):
    """
    Domain model representing a deterministic, actionable step required to 
    migrate a vulnerable cryptographic asset to a post-quantum or secure standard.
    """
    recommendation_id: UUID = Field(default_factory=uuid4)
    asset_id: UUID
    algorithm: str
    risk_score: int
    severity: Severity
    recommended_algorithm: str
    priority: Priority
    rationale: str
