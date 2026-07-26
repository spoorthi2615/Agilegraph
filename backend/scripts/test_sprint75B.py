import os
import sys
import logging
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.sensitivity.sensitivity_config import SensitivityConfig
from app.sensitivity.weight_perturbation import WeightPerturbator
from app.sensitivity.stability_metrics import StabilityMetrics
from app.sensitivity.ranking_stability import RankingStabilityEngine, RankingStabilityResult
from app.sensitivity.sensitivity_report import SensitivityReport

from app.dashboard.dashboard_models import DashboardPayload, SensitivityAnalysisMetrics
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.providers import (
    GraphRepository, MLProvider, ExplainabilityProvider,
    ExperimentProvider, ReportProvider, HeuristicsProvider, RecommendationProvider,
    SensitivityProvider
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint75B():
    logging.info("Testing Sprint 75B Sensitivity Analysis Framework...")
    
    # 1. Weight Perturbator
    perturbator = WeightPerturbator()
    base_weights = {"algorithm_strength": 0.4, "exposure": 0.2}
    
    single_perturbations = perturbator.generate_single_weight_perturbations(base_weights, [0.10, -0.10])
    
    # Expect 4 perturbations (2 weights * 2 scales)
    assert len(single_perturbations) == 4
    
    # Check +10% on algorithm_strength: 0.4 * 1.1 = 0.44
    alg_up = next(p for p in single_perturbations if p.id == "algorithm_strength_scale_0.1")
    assert round(alg_up.weights["algorithm_strength"], 2) == 0.44
    assert alg_up.weights["exposure"] == 0.2 # remains unchanged
    
    all_perturbations = perturbator.generate_all_weights_perturbations(base_weights, [0.10])
    assert len(all_perturbations) == 1
    assert round(all_perturbations[0].weights["algorithm_strength"], 2) == 0.44
    assert round(all_perturbations[0].weights["exposure"], 2) == 0.22
    
    logging.info("Weight perturbation logic verified.")
    
    # 2. Stability Metrics (Spearman & Top-K)
    base_ranks = ["A", "B", "C", "D", "E"]
    # B and C swapped
    pert_ranks = ["A", "C", "B", "D", "E"]
    
    rho = StabilityMetrics.spearman_rank_correlation(base_ranks, pert_ranks)
    assert rho > 0.8 # Highly correlated, just one adjacent swap
    
    top_3_overlap = StabilityMetrics.top_k_overlap(base_ranks, pert_ranks, k=3)
    assert top_3_overlap == 1.0 # The set {A,B,C} is identical, even if internal order changed
    
    logging.info("Non-parametric stability metrics (Spearman Rho, Top-K) verified.")
    
    # 3. Ranking Stability Engine
    engine = RankingStabilityEngine()
    result = engine.calculate_stability("test_pert", base_ranks, pert_ranks)
    
    assert result.max_rank_difference == 1 # B moved 1, C moved 1
    assert result.mean_rank_difference == 0.4 # 2/5 elements moved 1 spot each = 2/5 = 0.4
    logging.info("Ranking stability calculation verified.")
    
    # 4. JSON Report Generation
    report_json = SensitivityReport.generate_json([result])
    assert "test_pert" in report_json
    assert "spearman_rho" in report_json
    logging.info("Sensitivity JSON reporting verified.")
    
    # 5. Dashboard Integration
    mock_sens = MagicMock(spec=SensitivityProvider)
    mock_metrics = SensitivityAnalysisMetrics(
        overall_stability_score=0.92,
        most_sensitive_heuristic="certificate_weakness",
        most_stable_heuristic="migration_effort"
    )
    mock_sens.get_sensitivity_metrics.return_value = mock_metrics
    
    service = DashboardService(
        graph_repo=MagicMock(spec=GraphRepository),
        ml_provider=MagicMock(spec=MLProvider),
        explain_provider=MagicMock(spec=ExplainabilityProvider),
        experiment_provider=MagicMock(spec=ExperimentProvider),
        report_provider=MagicMock(spec=ReportProvider),
        heuristics_provider=MagicMock(spec=HeuristicsProvider),
        recommendation_provider=MagicMock(spec=RecommendationProvider),
        sensitivity_provider=mock_sens
    )
    
    payload = service.generate_dashboard_payload()
    assert payload.sensitivity_analysis.overall_stability_score == 0.92
    assert payload.sensitivity_analysis.most_sensitive_heuristic == "certificate_weakness"
    logging.info("Dashboard integration with Sensitivity data verified.")
    
    logging.info("All Sprint 75B Tests passed successfully!")

if __name__ == "__main__":
    test_sprint75B()
