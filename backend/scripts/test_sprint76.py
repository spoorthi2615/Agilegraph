import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.validation.e2e_validator import PipelineValidator
from app.validation.fault_injector import ChaosEngine
from app.validation.performance_tracker import MetricsTracker
from app.validation.validation_report import ValidationReportGenerator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint76():
    logging.info("Testing Sprint 76 End-to-End System Validation...")
    
    # Happy Path
    validator = PipelineValidator()
    result = validator.execute_dry_run()
    assert result.failed_stages == 0
    assert result.total_stages == 28
    
    metrics = MetricsTracker.extract_metrics(result)
    assert metrics.total_execution_time_ms > 0
    
    json_out = ValidationReportGenerator.generate_json(result, metrics)
    assert "validation_summary" in json_out
    logging.info("Happy path full E2E pipeline execution simulated successfully.")
    
    # Fault Injection Path (Graceful Degradation)
    chaos = ChaosEngine(failure_points=["Semgrep Integration", "Certificate Transparency Scanner"], skip_points=["Ablation Study"])
    chaos_result = validator.execute_dry_run(chaos_engine=chaos)
    
    assert chaos_result.failed_stages == 2
    assert chaos_result.skipped_stages == 1
    assert chaos_result.passed_stages == 25
    logging.info("ChaosEngine fault injection gracefully handled without cascading failures.")
    
    logging.info("AgileGraph End-to-End validation completed successfully.")
    logging.info("All Sprint 76 Tests passed successfully!")
    logging.info("=== AGILEGRAPH PRODUCTION READINESS VERIFIED ===")

if __name__ == "__main__":
    test_sprint76()
