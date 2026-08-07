import json

from app.validation.e2e_validator import ValidationResult
from app.validation.performance_tracker import PerformanceMetrics


class ValidationReportGenerator:
    @staticmethod
    def generate_json(result: ValidationResult, metrics: PerformanceMetrics) -> str:
        report = {
            "validation_summary": result.model_dump(),
            "performance_metrics": metrics.model_dump(),
        }
        return json.dumps(report, indent=2)
