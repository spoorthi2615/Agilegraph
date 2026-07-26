from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.heuristics.heuristic_breakdown import HeuristicBreakdown
from app.heuristics.recommendation_engine import MigrationRecommendation

class OverviewMetrics(BaseModel):
    total_repositories: int = 0
    total_crypto_assets: int = 0
    total_certificates: int = 0
    total_dependencies: int = 0
    total_vulnerabilities: int = 0
    total_findings: int = 0
    overall_risk_score: float = 0.0
    scan_timestamp: str = ""

class PQCReadinessMetrics(BaseModel):
    total_rsa_assets: int = 0
    total_ecc_assets: int = 0
    total_pqc_ready_assets: int = 0
    migration_priority_score: float = 0.0
    risk_score_by_algorithm: Dict[str, float] = Field(default_factory=dict)
    algorithm_migration_progress: float = 0.0

class MLEvaluationMetrics(BaseModel):
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0

class ExplanationSummary(BaseModel):
    node_id: int
    predicted_class: int
    confidence: float
    top_features: List[str] = Field(default_factory=list)
    top_edges: List[str] = Field(default_factory=list)

class ExperimentMetrics(BaseModel):
    bootstrap_lower_ci: float = 0.0
    bootstrap_upper_ci: float = 0.0
    permutation_p_value: float = 1.0
    cohens_kappa: float = 0.0
    fleiss_kappa: float = 0.0

class MoscaReadinessMetrics(BaseModel):
    # Placeholder for Mosca Readiness Index as requested in the synopsis
    mosca_score: float = 0.0
    mosca_compliance_percentage: float = 0.0
    
class DashboardPayload(BaseModel):
    """
    Unified API response payload containing the aggregated state for the React Frontend components.
    """
    overview: OverviewMetrics = Field(default_factory=OverviewMetrics)
    pqc_readiness: PQCReadinessMetrics = Field(default_factory=PQCReadinessMetrics)
    ml_metrics: MLEvaluationMetrics = Field(default_factory=MLEvaluationMetrics)
    explanations: List[ExplanationSummary] = Field(default_factory=list)
    experiments: ExperimentMetrics = Field(default_factory=ExperimentMetrics)
    reports_available: List[str] = Field(default_factory=list)
    heuristic_breakdowns: List[HeuristicBreakdown] = Field(default_factory=list)
    migration_recommendations: List[MigrationRecommendation] = Field(default_factory=list)
    mosca_readiness: MoscaReadinessMetrics = Field(default_factory=MoscaReadinessMetrics)
