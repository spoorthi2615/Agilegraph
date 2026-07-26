from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any

class ExpertAgreement(BaseModel):
    """
    Domain model representing the mathematical consensus and variance across 
    a panel of human cybersecurity experts assessing a single graph node.
    """
    agreement_id: UUID = Field(default_factory=uuid4)
    node_id: str
    
    total_experts: int
    agreement_percentage: float
    majority_label: int
    consensus_reached: bool
    
    expert_labels: List[int]
    expert_scores: List[float]
    average_score: float
    score_variance: float
    
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
