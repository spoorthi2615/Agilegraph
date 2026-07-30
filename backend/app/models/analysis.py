from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class AnalysisBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class RiskRecommendation(AnalysisBaseModel):
    category: str
    score: int
    hint: str

class MigrationRecommendationDTO(AnalysisBaseModel):
    target_algorithm: str
    estimated_days: int
    risk_reduction: int
    steps: List[str]

class CertificateSummary(AnalysisBaseModel):
    name: str
    type: str

class DependencySummary(AnalysisBaseModel):
    name: str
    type: str

class AlgorithmSummary(AnalysisBaseModel):
    name: str
    count: int

class ConnectedAsset(AnalysisBaseModel):
    id: str
    name: str
    algorithm: str
    risk: str

class ExplainabilitySummary(AnalysisBaseModel):
    feature_importance: List[dict] = Field(default_factory=list)
    important_edges: List[dict] = Field(default_factory=list)
    confidence: float = Field(default=0.0)
    natural_language_explanation: str = Field(default="")

class AssetSummary(AnalysisBaseModel):
    id: str
    name: str
    type: str
    department: str
    algorithm: str
    key_size: str
    risk_score: int
    risk: str
    recommended: str
    migration_days: int
    risk_reduction: int
    status: str
    priority: int
    discovered_at: str
    location: str
    connections: List[str] = Field(default_factory=list)
    description: str

class AssetDetail(AssetSummary):
    heuristic_breakdown: List[RiskRecommendation] = Field(default_factory=list)
    connected_assets: List[ConnectedAsset] = Field(default_factory=list)
    dependencies: List[DependencySummary] = Field(default_factory=list)
    certificates: List[CertificateSummary] = Field(default_factory=list)
    migration_projection: Optional[MigrationRecommendationDTO] = None
    explainability: Optional[ExplainabilitySummary] = None

class PaginatedAssetResponse(AnalysisBaseModel):
    items: List[AssetSummary]
    total: int
    page: int
    size: int
    total_pages: int
