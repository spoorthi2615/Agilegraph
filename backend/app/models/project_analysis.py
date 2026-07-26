from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field

from app.models.language import DetectedLanguage
from app.scanners.scanner_result import ScannerResult

class ProjectAnalysisResult(BaseModel):
    """
    Orchestration output model containing language detection results,
    executed scanners, and the combined findings across all executed scanners.
    """
    project_id: str
    detected_languages: List[DetectedLanguage]
    executed_scanners: List[str]
    scanner_results: List[ScannerResult]
    total_findings: int
    total_errors: int
    analysis_completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
