from typing import List

from pydantic import BaseModel


class DatasetSummary(BaseModel):
    total_repositories: int
    programming_languages: List[str]
    size_categories: List[str]
    total_crypto_assets: int
    total_certificates: int
    total_dependencies: int
    total_nodes: int
    total_edges: int


class ScannerCompliance(BaseModel):
    java_implemented: bool
    python_implemented: bool
    go_implemented: bool
    dependency_implemented: bool
    certificate_implemented: bool
    live_tls_implemented: bool
    ct_implemented: bool
    semgrep_implemented: bool
    cbom_implemented: bool


class GraphCompliance(BaseModel):
    node_types_verified: bool
    edge_types_verified: bool
    graph_builder_active: bool
    risk_propagation_active: bool
    schema_compliant: bool


class MLCompliance(BaseModel):
    training_implemented: bool
    inference_implemented: bool
    evaluation_implemented: bool
    benchmarking_implemented: bool
    ablation_implemented: bool
    explainability_implemented: bool


class DashboardCompliance(BaseModel):
    overview_implemented: bool
    graph_implemented: bool
    ml_implemented: bool
    explainability_implemented: bool
    benchmark_implemented: bool
    statistics_implemented: bool
    migration_intelligence_implemented: bool
    sensitivity_implemented: bool
    reports_implemented: bool


class ModuleStatus(BaseModel):
    name: str
    status: str  # "Implemented", "Partially Implemented", "Research-only", "Future Work"
    notes: str = ""


class ReadinessScore(BaseModel):
    architecture_readiness: float
    research_readiness: float
    implementation_readiness: float
    synopsis_compliance_percentage: float
    overall_readiness_score: float


class SynopsisComplianceReport(BaseModel):
    dataset_verification: DatasetSummary
    scanner_verification: ScannerCompliance
    graph_verification: GraphCompliance
    ml_verification: MLCompliance
    dashboard_verification: DashboardCompliance
    synopsis_cross_check: List[ModuleStatus]
    production_readiness: ReadinessScore
