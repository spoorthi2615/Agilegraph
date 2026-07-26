import os
import sys
import logging
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.dashboard.dashboard_models import (
    DashboardPayload, OverviewMetrics, PQCReadinessMetrics,
    MLEvaluationMetrics, ExplanationSummary, ExperimentMetrics
)
from app.dashboard.providers import (
    GraphRepository, MLProvider, ExplainabilityProvider,
    ExperimentProvider, ReportProvider
)
from app.dashboard.dashboard_service import DashboardService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint76_dashboard_aggregation():
    logging.info("Testing Sprint 75 Dashboard Aggregation Engine...")
    
    # 1. Setup Happy Path Mocks
    mock_graph = MagicMock(spec=GraphRepository)
    mock_graph.get_overview_metrics.return_value = OverviewMetrics(total_crypto_assets=100)
    mock_graph.get_pqc_readiness.return_value = PQCReadinessMetrics(total_rsa_assets=50, total_pqc_ready_assets=5)
    
    mock_ml = MagicMock(spec=MLProvider)
    mock_ml.get_evaluation_metrics.return_value = MLEvaluationMetrics(accuracy=0.92)
    
    mock_explain = MagicMock(spec=ExplainabilityProvider)
    mock_explain.get_recent_explanations.return_value = [
        ExplanationSummary(node_id=1, predicted_class=1, confidence=0.95, top_features=["key_size"])
    ]
    
    mock_exp = MagicMock(spec=ExperimentProvider)
    mock_exp.get_experiment_metrics.return_value = ExperimentMetrics(cohens_kappa=0.88)
    
    mock_rep = MagicMock(spec=ReportProvider)
    mock_rep.get_available_reports.return_value = ["sprint_70_semgrep.json"]
    
    service = DashboardService(mock_graph, mock_ml, mock_explain, mock_exp, mock_rep)
    
    payload = service.generate_dashboard_payload()
    
    # Assertions for Happy Path
    assert payload.overview.total_crypto_assets == 100
    assert payload.pqc_readiness.total_pqc_ready_assets == 5
    assert payload.ml_metrics.accuracy == 0.92
    assert len(payload.explanations) == 1
    assert payload.experiments.cohens_kappa == 0.88
    assert "sprint_70_semgrep.json" in payload.reports_available
    logging.info("Happy path aggregation succeeded. Data contracts verified.")
    
    # 2. Setup Fault Tolerance Path
    faulty_graph = MagicMock(spec=GraphRepository)
    faulty_graph.get_overview_metrics.side_effect = Exception("Neo4j timeout")
    faulty_graph.get_pqc_readiness.side_effect = Exception("Graph disconnected")
    
    faulty_ml = MagicMock(spec=MLProvider)
    faulty_ml.get_evaluation_metrics.side_effect = Exception("GATv2 model missing")
    
    faulty_explain = MagicMock(spec=ExplainabilityProvider)
    faulty_explain.get_recent_explanations.side_effect = Exception("No gradients")
    
    faulty_exp = MagicMock(spec=ExperimentProvider)
    faulty_exp.get_experiment_metrics.side_effect = Exception("Bootstrap data missing")
    
    faulty_rep = MagicMock(spec=ReportProvider)
    faulty_rep.get_available_reports.side_effect = Exception("S3 bucket offline")
    
    fault_tolerant_service = DashboardService(
        faulty_graph, faulty_ml, faulty_explain, faulty_exp, faulty_rep
    )
    
    logging.info("Testing Graceful Degradation (All providers unavailable)...")
    safe_payload = fault_tolerant_service.generate_dashboard_payload()
    
    # Assertions for Graceful Degradation
    assert isinstance(safe_payload, DashboardPayload)
    assert safe_payload.overview.total_crypto_assets == 0 # Default safe fallback
    assert safe_payload.pqc_readiness.total_rsa_assets == 0
    assert safe_payload.ml_metrics.accuracy == 0.0
    assert safe_payload.experiments.cohens_kappa == 0.0
    assert len(safe_payload.explanations) == 0
    assert len(safe_payload.reports_available) == 0
    
    logging.info("Graceful degradation succeeded! The dashboard API will not crash when dependent microservices fail.")
    logging.info("All Sprint 75 Dashboard tests passed successfully!")

if __name__ == "__main__":
    test_sprint76_dashboard_aggregation()
