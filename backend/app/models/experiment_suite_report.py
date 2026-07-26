from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.models.experiment_execution_report import ExperimentExecutionReport

class ExperimentSuiteReport(BaseModel):
    """
    Domain model representing the aggregation of multiple AgileGraph experiments 
    into a single, comprehensive suite report suitable for dissertation-level 
    evaluation.
    """
    suite_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    suite_name: str
    suite_description: str
    
    experiment_reports: List[ExperimentExecutionReport]
    
    total_experiments: int
    successful_experiments: int
    tied_experiments: int
    failed_experiments: int
    
    success_rate: float
    
    overall_summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
