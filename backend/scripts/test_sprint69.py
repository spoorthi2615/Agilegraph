import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.workflow.workflow_config import WorkflowConfig
from app.experiments.workflow.experiment_workflow import ExperimentWorkflow
from app.experiments.workflow.workflow_report import WorkflowReport

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint69():
    logging.info("Testing Sprint 69 Master Experimental Workflow...")
    
    config = WorkflowConfig(output_directory="outputs/workflow")
    
    # 1. Complete Workflow Execution
    logging.info("\n--- TEST 1: Full Execution ---")
    workflow_full = ExperimentWorkflow(config)
    res_full = workflow_full.execute()
    
    assert "Benchmark Execution" in res_full.execution_times
    assert "Expert Validation & Reliability" in res_full.execution_times
    assert not res_full.errors, "Full execution should not have errors"
    
    WorkflowReport.generate(res_full, config.output_directory)
    logging.info("Full workflow execution and reporting passed.")
    
    # 2. Partial Workflow (Isolated Fault Injection)
    logging.info("\n--- TEST 2: Fault Tolerance ---")
    config_partial = WorkflowConfig(output_directory="outputs/workflow")
    workflow_partial = ExperimentWorkflow(config_partial)
    
    # Inject a fault artificially to ensure it doesn't crash the orchestrator
    def failing_phase():
        raise ValueError("Missing critical experimental dataset")
        
    workflow_partial._run_phase("Data Ingestion", failing_phase)
    res_partial = workflow_partial.execute()
    
    assert "Data Ingestion" in res_partial.errors
    assert res_partial.errors["Data Ingestion"] == "Missing critical experimental dataset"
    assert "Expert Validation & Reliability" in res_partial.execution_times, "Orchestrator crashed instead of isolating fault!"
    
    WorkflowReport.generate(res_partial, config.output_directory)
    logging.info("Fault-tolerant workflow execution and reporting passed.")
    
    logging.info("All Sprint 69 Master Workflow tests passed successfully!")

if __name__ == "__main__":
    test_sprint69()
