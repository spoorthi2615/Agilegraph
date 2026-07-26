from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum

from app.models.benchmark_report import BenchmarkReport
from app.models.ablation_study_report import AblationStudyReport


class ExperimentStatus(str, Enum):
    """
    Strictly typed enumeration defining the possible terminal states of an experiment.
    """
    SUCCESS = "SUCCESS"
    FAILURE_BASELINE_RETAINED = "FAILURE_BASELINE_RETAINED"
    STATISTICAL_TIE = "STATISTICAL_TIE"


class ExperimentExecutionReport(BaseModel):
    """
    Domain model representing the complete, macroscopic orchestration of a single 
    AgileGraph experiment, packaging all benchmarks and ablation studies into a 
    unified, dissertation-ready payload.
    """
    execution_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    experiment_name: str
    experiment_description: str
    
    benchmark_report: BenchmarkReport
    ablation_reports: List[AblationStudyReport]
    
    overall_result: ExperimentStatus
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
