from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class ExplainabilityBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class FeatureImportance(ExplainabilityBaseModel):
    feature_name: str
    contribution: float = Field(default=0.0)
    normalized_weight: float = Field(default=0.0)
    positive_influence: bool = Field(default=True)

class ImportantEdge(ExplainabilityBaseModel):
    source_node: str
    target_node: str
    relationship: str
    importance_score: float = Field(default=0.0)
    confidence: float = Field(default=0.0)

class GNNExplanation(ExplainabilityBaseModel):
    feature_importance: List[FeatureImportance] = Field(default_factory=list)
    important_edges: List[ImportantEdge] = Field(default_factory=list)

class HeuristicBreakdown(ExplainabilityBaseModel):
    risk_formula_breakdown: str = Field(default="")
    weight_contribution: float = Field(default=0.0)
    penalty_breakdown: str = Field(default="")
    algorithm_score: int = Field(default=0)
    certificate_score: int = Field(default=0)
    exposure_score: int = Field(default=0)
    graph_centrality_score: int = Field(default=0)

class HeuristicExplanation(ExplainabilityBaseModel):
    breakdown: HeuristicBreakdown = Field(default_factory=HeuristicBreakdown)

class MigrationImpact(ExplainabilityBaseModel):
    recommended_pqc_algorithm: str = Field(default="")
    estimated_risk_reduction: int = Field(default=0)
    migration_priority: int = Field(default=0)
    migration_effort: int = Field(default=0)
    expected_readiness_improvement: int = Field(default=0)

class ConfidenceMetrics(ExplainabilityBaseModel):
    overall_confidence: float = Field(default=0.0)
    model_certainty: float = Field(default=0.0)
    data_quality_score: float = Field(default=0.0)

class ExplanationMetadata(ExplainabilityBaseModel):
    generated_at: str = Field(default="")
    model_version: str = Field(default="1.0")

class AssetInformation(ExplainabilityBaseModel):
    asset_id: str
    name: str = Field(default="Unknown Asset")
    type: str = Field(default="service")
    algorithm: str = Field(default="Unknown")
    overall_risk: int = Field(default=0)
    overall_confidence: float = Field(default=0.0)

class ExplainabilityResponse(ExplainabilityBaseModel):
    asset_information: AssetInformation
    gnn_explanation: GNNExplanation = Field(default_factory=GNNExplanation)
    heuristic_explanation: HeuristicExplanation = Field(default_factory=HeuristicExplanation)
    migration_recommendation: MigrationImpact = Field(default_factory=MigrationImpact)
    confidence_metrics: ConfidenceMetrics = Field(default_factory=ConfidenceMetrics)
    natural_language_summary: str = Field(default="")
    metadata: ExplanationMetadata = Field(default_factory=ExplanationMetadata)
