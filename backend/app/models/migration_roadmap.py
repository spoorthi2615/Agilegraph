from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone

class MigrationRoadmap(BaseModel):
    """
    Domain model representing an organization-level strategic roadmap for 
    migrating vulnerable cryptographic assets to secure or Post-Quantum Cryptography.
    """
    roadmap_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    readiness_score: float
    readiness_level: str
    total_recommendations: int
    immediate_actions: int
    high_priority_actions: int
    medium_priority_actions: int
    low_priority_actions: int
    estimated_phases: int
    executive_summary: str
