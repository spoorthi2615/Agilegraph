from pydantic import BaseModel
from app.validation.e2e_validator import ValidationResult

class PerformanceMetrics(BaseModel):
    total_execution_time_ms: float
    scanner_time_ms: float
    graph_construction_time_ms: float
    inference_time_ms: float
    dashboard_generation_time_ms: float

class MetricsTracker:
    @staticmethod
    def extract_metrics(result: ValidationResult) -> PerformanceMetrics:
        total = sum(s.execution_time_ms for s in result.stages)
        scanners = sum(s.execution_time_ms for s in result.stages if "Scanner" in s.stage_name or "Integration" in s.stage_name)
        graph = sum(s.execution_time_ms for s in result.stages if "Graph" in s.stage_name)
        inference = sum(s.execution_time_ms for s in result.stages if "GATv2" in s.stage_name or "Explainability" in s.stage_name)
        dash = sum(s.execution_time_ms for s in result.stages if "Dashboard" in s.stage_name)
        
        return PerformanceMetrics(
            total_execution_time_ms=total,
            scanner_time_ms=scanners,
            graph_construction_time_ms=graph,
            inference_time_ms=inference,
            dashboard_generation_time_ms=dash
        )
