from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any

class SignificanceTestResult(BaseModel):
    """
    Domain model representing the mathematical result of a statistical 
    significance test between two experimental conditions (e.g., a baseline AI 
    model vs. a newly trained AI model).
    """
    test_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    metric_name: str
    
    baseline_mean: float
    comparison_mean: float
    mean_difference: float
    
    test_name: str
    test_statistic: float
    p_value: float
    alpha: float
    
    statistically_significant: bool
    effect_size: float
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
