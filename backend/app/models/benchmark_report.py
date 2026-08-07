from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.bootstrap_confidence_interval import BootstrapConfidenceInterval
from app.models.significance_test_result import SignificanceTestResult


class BenchmarkReport(BaseModel):
    """
    Domain model representing the macroscopic orchestration and comparison
    between a baseline approach (e.g., GraphSAGE) and a new experimental
    approach (e.g., GATv2).
    """

    benchmark_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    metric_name: str

    baseline_name: str
    comparison_name: str

    baseline_value: float
    comparison_value: float

    improvement: float
    relative_improvement: float

    confidence_interval: Optional[BootstrapConfidenceInterval]
    significance_test: Optional[SignificanceTestResult]

    winner: str

    metadata: Dict[str, Any] = Field(default_factory=dict)
