import os
import sys
import logging
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.statistics.statistics_config import StatisticsConfig
from app.experiments.statistics.bootstrap_service import BootstrapService
from app.experiments.statistics.confidence_interval_report import ConfidenceIntervalReport

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint64():
    logging.info("Testing Sprint 64 Statistical Confidence Interval Framework...")
    
    config = StatisticsConfig(
        bootstrap_iterations=2000,
        confidence_level=0.95,
        random_seed=42,
        output_directory="outputs/statistics"
    )
    
    service = BootstrapService(config)
    
    # Generate mock distribution data: e.g. accuracy scores across 30 repositories
    mock_accuracies = [0.82, 0.84, 0.85, 0.88, 0.81, 0.86, 0.85, 0.89, 0.90, 0.83, 
                       0.84, 0.86, 0.87, 0.84, 0.85, 0.82, 0.89, 0.88, 0.81, 0.85,
                       0.86, 0.85, 0.84, 0.83, 0.87, 0.88, 0.89, 0.82, 0.81, 0.84]
                       
    mock_f1 = [x - 0.02 for x in mock_accuracies]
    
    # 1. Estimate Intervals
    metrics_data = {
        "Accuracy": mock_accuracies,
        "Macro F1": mock_f1
    }
    
    result = service.estimate_experiment_intervals("Full Model (Mock)", metrics_data)
    
    # 2. Verify Result Structure
    assert result.experiment_name == "Full Model (Mock)"
    assert "Accuracy" in result.metrics
    assert "Macro F1" in result.metrics
    
    # 3. Verify Mathematical correctness logic (bounds check)
    acc_ci = result.metrics["Accuracy"]
    assert acc_ci.lower_bound <= acc_ci.mean <= acc_ci.upper_bound, "Mean is not between confidence bounds!"
    assert acc_ci.bootstrap_iterations == 2000
    
    logging.info(f"Accuracy {config.confidence_level*100:.1f}% CI: [{acc_ci.lower_bound:.4f}, {acc_ci.upper_bound:.4f}]")
    logging.info(f"F1       {config.confidence_level*100:.1f}% CI: [{result.metrics['Macro F1'].lower_bound:.4f}, {result.metrics['Macro F1'].upper_bound:.4f}]")
    
    # 4. Generate Reports
    ConfidenceIntervalReport.generate([result], config.output_directory)
    
    # 5. Invalid handling test
    try:
        service.estimate_confidence_interval("Empty", [])
        assert False, "Should have raised ValueError for empty list"
    except ValueError:
        logging.info("Properly caught empty dataset exception.")
        
    logging.info("All Sprint 64 Statistical Confidence Interval tests passed successfully!")

if __name__ == "__main__":
    test_sprint64()
