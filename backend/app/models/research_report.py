from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.models.experiment_suite_report import ExperimentSuiteReport


class ResearchReport(BaseModel):
    """
    Domain model representing the absolute highest tier of the AgileGraph evaluation 
    hierarchy, wrapping a massive Experiment Suite into a final, human-readable 
    publication-ready payload.
    """
    report_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    report_title: str
    report_description: str
    
    experiment_suite_report: ExperimentSuiteReport
    
    executive_summary: str
    key_findings: List[str]
    recommendations: List[str]
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
