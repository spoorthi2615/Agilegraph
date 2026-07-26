from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any

from app.models.benchmark_report import BenchmarkReport

class AblationStudyReport(BaseModel):
    """
    Domain model representing the macroscopic orchestration and comparison 
    of an ablation study, measuring the statistical impact of removing a 
    specific component from the system architecture.
    """
    study_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    experiment_name: str
    component_name: str
    
    baseline_metric: float
    ablated_metric: float
    
    performance_drop: float
    relative_drop: float
    
    component_importance: str
    
    benchmark_report: BenchmarkReport
    
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
