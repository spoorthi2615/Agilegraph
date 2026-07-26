from abc import ABC, abstractmethod
from typing import List, Optional
from app.dashboard.dashboard_models import (
    OverviewMetrics, PQCReadinessMetrics, MLEvaluationMetrics,
    ExplanationSummary, ExperimentMetrics
)
from app.heuristics.heuristic_breakdown import HeuristicBreakdown
from app.heuristics.recommendation_engine import MigrationRecommendation

class GraphRepository(ABC):
    """Abstract interface for querying raw structural knowledge graph state."""
    @abstractmethod
    def get_overview_metrics(self) -> Optional[OverviewMetrics]: pass
    
    @abstractmethod
    def get_pqc_readiness(self) -> Optional[PQCReadinessMetrics]: pass

class MLProvider(ABC):
    """Abstract interface for fetching GATv2 evaluation artifacts."""
    @abstractmethod
    def get_evaluation_metrics(self) -> Optional[MLEvaluationMetrics]: pass

class ExplainabilityProvider(ABC):
    """Abstract interface for fetching PyG GNNExplainer outputs."""
    @abstractmethod
    def get_recent_explanations(self, limit: int = 5) -> List[ExplanationSummary]: pass

class ExperimentProvider(ABC):
    """Abstract interface for statistical bounds and inter-rater reliability metrics."""
    @abstractmethod
    def get_experiment_metrics(self) -> Optional[ExperimentMetrics]: pass

class ReportProvider(ABC):
    """Abstract interface exposing raw JSON/Markdown report download links."""
    @abstractmethod
    def get_available_reports(self) -> List[str]: pass

class HeuristicsProvider(ABC):
    """Abstract interface exposing heuristic breakdown data."""
    @abstractmethod
    def get_heuristic_breakdowns(self, limit: int = 10) -> List[HeuristicBreakdown]: pass

class RecommendationProvider(ABC):
    """Abstract interface exposing prioritized migration data."""
    @abstractmethod
    def get_migration_recommendations(self, limit: int = 10) -> List[MigrationRecommendation]: pass

class SensitivityProvider(ABC):
    """Abstract interface exposing stability analysis data."""
    @abstractmethod
    def get_sensitivity_metrics(self) -> Optional['SensitivityAnalysisMetrics']: pass
