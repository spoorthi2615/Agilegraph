from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any

class BootstrapConfidenceInterval(BaseModel):
    """
    Domain model representing the mathematical boundaries and statistical 
    confidence metrics of a specific model evaluation.
    """
    interval_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    metric_name: str
    point_estimate: float
    confidence_level: float
    
    lower_bound: float
    upper_bound: float
    
    num_bootstrap_samples: int
    bootstrap_mean: float
    bootstrap_std: float
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
