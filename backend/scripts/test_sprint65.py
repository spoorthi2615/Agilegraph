import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.significance.significance_config import SignificanceConfig
from app.experiments.significance.significance_test_service import SignificanceTestService
from app.experiments.significance.significance_report import SignificanceReport

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint65():
    logging.info("Testing Sprint 65 Statistical Significance Testing Framework...")
    
    config = SignificanceConfig(
        permutations=5000, # Using 5k for faster test execution
        alpha=0.05,
        random_seed=42,
        output_directory="outputs/significance"
    )
    
    service = SignificanceTestService(config)
    
    # Scenario A: AgileGraph performs significantly better than Baseline
    agilegraph_metrics = [0.85, 0.88, 0.90, 0.84, 0.87, 0.89, 0.86, 0.91, 0.88, 0.89, 0.85, 0.84, 0.87, 0.90, 0.86]
    baseline_metrics   = [0.80, 0.81, 0.82, 0.79, 0.80, 0.83, 0.78, 0.81, 0.80, 0.82, 0.79, 0.78, 0.81, 0.82, 0.80]
    
    # Scenario B: AgileGraph is practically identical to a clone model
    identical_metrics  = [0.84, 0.88, 0.91, 0.83, 0.86, 0.89, 0.85, 0.92, 0.87, 0.90, 0.86, 0.83, 0.88, 0.89, 0.85]
    
    # 1. Test Clear Improvement (Should Reject H0)
    result_a = service.test_significance(
        "AgileGraph", "RuleBased", "Accuracy", agilegraph_metrics, baseline_metrics
    )
    
    assert result_a.decision == "Reject H0", f"Expected Reject H0 for clear improvement, got {result_a.decision}"
    assert result_a.p_value < 0.05, "p-value should be statistically significant (< 0.05)"
    
    # 2. Test Identical Models (Should Fail to Reject H0)
    result_b = service.test_significance(
        "AgileGraph", "AgileGraph_Clone", "Accuracy", agilegraph_metrics, identical_metrics
    )
    
    assert result_b.decision == "Fail to Reject H0", f"Expected Fail to Reject H0 for identical models, got {result_b.decision}"
    assert result_b.p_value > 0.05, "p-value should not be significant (> 0.05)"
    
    logging.info(f"Scenario A (Clear Win): Obs Diff: {result_a.observed_difference:.4f}, p-value: {result_a.p_value:.6f} -> {result_a.decision}")
    logging.info(f"Scenario B (Tie): Obs Diff: {result_b.observed_difference:.4f}, p-value: {result_b.p_value:.6f} -> {result_b.decision}")
    
    # 3. Generate Reports
    SignificanceReport.generate([result_a, result_b], config.output_directory)
    
    # 4. Invalid handling test (empty arrays)
    try:
        service.test_significance("A", "B", "Metric", [], [])
        assert False, "Should have raised ValueError for empty list"
    except ValueError:
        logging.info("Properly caught empty dataset exception.")
        
    logging.info("All Sprint 65 Statistical Significance tests passed successfully!")

if __name__ == "__main__":
    test_sprint65()
