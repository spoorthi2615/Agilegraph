import os
import sys
import logging
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.heuristics.heuristic_breakdown import HeuristicBreakdown
from app.heuristics.heuristic_explainer import HeuristicExplainer
from app.heuristics.migration_estimator import MigrationEstimator
from app.heuristics.recommendation_engine import RecommendationEngine

from app.dashboard.dashboard_models import DashboardPayload
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.providers import (
    GraphRepository, MLProvider, ExplainabilityProvider,
    ExperimentProvider, ReportProvider, HeuristicsProvider, RecommendationProvider
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint75A():
    logging.info("Testing Sprint 75A Heuristic Explainability & Migration Engine...")
    
    # 1. Heuristic Explainer
    explainer = HeuristicExplainer()
    raw_payload = {
        "total_score": 75.0,
        "is_pqc_ready": False,
        "factors": {
            "algorithm_strength": 40.0,
            "certificate_weakness": 15.0,
            "graph_centrality": 20.0
        }
    }
    breakdown = explainer.decompose_score("RSA_Key_01", raw_payload)
    
    assert breakdown.total_score == 75.0
    assert breakdown.algorithm_strength_penalty == 40.0
    assert breakdown.certificate_weakness_penalty == 15.0
    logging.info("Heuristic decomposition verified.")
    
    # 2. Migration Estimator
    estimator = MigrationEstimator()
    reduction = estimator.estimate_reduction(
        current_total_score=breakdown.total_score,
        algorithm_penalty=breakdown.algorithm_strength_penalty,
        certificate_penalty=breakdown.certificate_weakness_penalty
    )
    
    # 75.0 - (40.0 + 15.0) = 20.0
    assert reduction.projected_risk == 20.0
    assert reduction.absolute_reduction == 55.0
    assert round(reduction.percentage_reduction, 1) == 73.3
    logging.info("Risk reduction mathematical estimation verified.")
    
    # 3. Recommendation Engine
    engine = RecommendationEngine()
    gnn_predictions = {"RSA_Key_01": 0.8} # High risk prediction from ML
    
    recommendations = engine.generate_recommendations([breakdown], gnn_predictions)
    assert len(recommendations) == 1
    rec = recommendations[0]
    
    # Priority = Absolute Reduction (55.0) * (1 + GNN Modifier (0.8)) = 99.0
    assert rec.priority_score == 99.0
    assert "Kyber" in rec.suggested_replacement
    logging.info("Recommendation prioritization and logic verified.")
    
    # 4. Dashboard Integration (Fault Tolerance & Aggregation)
    mock_heuristics = MagicMock(spec=HeuristicsProvider)
    mock_heuristics.get_heuristic_breakdowns.return_value = [breakdown]
    
    mock_rec = MagicMock(spec=RecommendationProvider)
    mock_rec.get_migration_recommendations.side_effect = Exception("Service offline")
    
    service = DashboardService(
        graph_repo=MagicMock(spec=GraphRepository),
        ml_provider=MagicMock(spec=MLProvider),
        explain_provider=MagicMock(spec=ExplainabilityProvider),
        experiment_provider=MagicMock(spec=ExperimentProvider),
        report_provider=MagicMock(spec=ReportProvider),
        heuristics_provider=mock_heuristics,
        recommendation_provider=mock_rec
    )
    
    payload = service.generate_dashboard_payload()
    assert isinstance(payload, DashboardPayload)
    assert len(payload.heuristic_breakdowns) == 1
    assert len(payload.migration_recommendations) == 0 # Defaults gracefully safely when provider throws
    assert payload.mosca_readiness.mosca_score == 0.0 # Placeholder logic verifies
    logging.info("Dashboard Sprint 75A integration and fault-tolerance verified.")
    
    logging.info("All Sprint 75A Tests passed successfully!")

if __name__ == "__main__":
    test_sprint75A()
