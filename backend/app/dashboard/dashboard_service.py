import logging
from typing import Optional
from app.dashboard.dashboard_models import (
    DashboardPayload, OverviewMetrics, PQCReadinessMetrics,
    MLEvaluationMetrics, ExperimentMetrics
)
from app.dashboard.providers import (
    GraphRepository, MLProvider, ExplainabilityProvider,
    ExperimentProvider, ReportProvider, HeuristicsProvider, RecommendationProvider,
    SensitivityProvider
)

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Facade aggregator for the AgileGraph Dashboard UI.
    Delegates all data retrieval to abstracted providers to maintain Clean Architecture.
    """
    def __init__(
        self,
        graph_repo: GraphRepository,
        ml_provider: MLProvider,
        explain_provider: ExplainabilityProvider,
        experiment_provider: ExperimentProvider,
        report_provider: ReportProvider,
        heuristics_provider: HeuristicsProvider = None,
        recommendation_provider: RecommendationProvider = None,
        sensitivity_provider: SensitivityProvider = None
    ):
        self.graph_repo = graph_repo
        self.ml_provider = ml_provider
        self.explain_provider = explain_provider
        self.experiment_provider = experiment_provider
        self.report_provider = report_provider
        self.heuristics_provider = heuristics_provider
        self.recommendation_provider = recommendation_provider
        self.sensitivity_provider = sensitivity_provider
        
    def generate_dashboard_payload(self) -> DashboardPayload:
        """
        Synthesizes a unified Dashboard payload.
        Implements strict graceful degradation.
        """
        payload = DashboardPayload()
        
        # 1. Graph Overview & PQC
        try:
            overview = self.graph_repo.get_overview_metrics()
            if overview: payload.overview = overview
            
            pqc = self.graph_repo.get_pqc_readiness()
            if pqc: payload.pqc_readiness = pqc
        except Exception as e:
            logger.error(f"GraphRepository failed to fetch data: {e}")
            
        # 2. ML Metrics
        try:
            ml_metrics = self.ml_provider.get_evaluation_metrics()
            if ml_metrics: payload.ml_metrics = ml_metrics
        except Exception as e:
            logger.error(f"MLProvider failed to fetch data: {e}")
            
        # 3. Explainability
        try:
            explanations = self.explain_provider.get_recent_explanations(limit=5)
            if explanations: payload.explanations = explanations
        except Exception as e:
            logger.error(f"ExplainabilityProvider failed to fetch data: {e}")
            
        # 4. Experiment Bounds
        try:
            experiments = self.experiment_provider.get_experiment_metrics()
            if experiments: payload.experiments = experiments
        except Exception as e:
            logger.error(f"ExperimentProvider failed to fetch data: {e}")
            
        # 5. Reports
        try:
            reports = self.report_provider.get_available_reports()
            if reports: payload.reports_available = reports
        except Exception as e:
            logger.error(f"ReportProvider failed to fetch data: {e}")

        # 6. Heuristics & Recommendations (Sprint 75A)
        if self.heuristics_provider:
            try:
                breakdowns = self.heuristics_provider.get_heuristic_breakdowns()
                if breakdowns: payload.heuristic_breakdowns = breakdowns
            except Exception as e:
                logger.error(f"HeuristicsProvider failed to fetch data: {e}")
                
        if self.recommendation_provider:
            try:
                recs = self.recommendation_provider.get_migration_recommendations()
                if recs: payload.migration_recommendations = recs
            except Exception as e:
                logger.error(f"RecommendationProvider failed to fetch data: {e}")
                
        # 7. Sensitivity Analysis (Sprint 75B)
        if self.sensitivity_provider:
            try:
                sens = self.sensitivity_provider.get_sensitivity_metrics()
                if sens: payload.sensitivity_analysis = sens
            except Exception as e:
                logger.error(f"SensitivityProvider failed to fetch data: {e}")
            
        return payload
