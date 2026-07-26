from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class ExpertValidation(BaseModel):
    """
    Domain model representing an empirical comparison between the AI's 
    predicted risk for a node and a human cybersecurity expert's assessment.
    """
    validation_id: UUID = Field(default_factory=uuid4)
    expert_id: str
    expert_name: str
    node_id: str
    
    # AI Predictions
    ai_risk_score: float
    ai_label: int
    
    # Expert Assessments
    expert_risk_score: float
    expert_label: int
    
    # Mathematical Comparison
    agreement: bool
    score_difference: float
    
    comments: Optional[str] = None
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
