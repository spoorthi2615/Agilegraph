from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class GraphBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class GraphNode(GraphBaseModel):
    id: str
    label: str
    type: str
    risk: str
    x: float = Field(default=0.0)
    y: float = Field(default=0.0)


class GraphEdge(GraphBaseModel):
    source: str
    target: str


class GraphMetadata(GraphBaseModel):
    generated_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    repository_name: str = Field(default="AgileGraph")
    graph_version: str = Field(default="1.0.0")
    graph_size: str = Field(default="0 KB")


class GraphStatistics(GraphBaseModel):
    total_nodes: int = Field(default=0)
    total_edges: int = Field(default=0)
    connected_components: int = Field(default=0)
    critical_assets: int = Field(default=0)
    high_risk_assets: int = Field(default=0)
    pqc_ready_assets: int = Field(default=0)
    average_degree: float = Field(default=0.0)
    graph_density: float = Field(default=0.0)


class GraphFilter(GraphBaseModel):
    repository: Optional[str] = None
    risk_level: Optional[str] = None
    severity: Optional[str] = None
    node_type: Optional[str] = None
    algorithm: Optional[str] = None
    pqc_status: Optional[str] = None


class GraphResponse(GraphBaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    statistics: GraphStatistics = Field(default_factory=GraphStatistics)
    metadata: GraphMetadata = Field(default_factory=GraphMetadata)
    filters: GraphFilter = Field(default_factory=GraphFilter)


class NodeRelationship(GraphBaseModel):
    id: str
    name: str
    type: str
    risk: str
    relationship_type: str


class NodeDetails(GraphBaseModel):
    id: str
    name: str
    type: str
    department: str
    algorithm: str
    key_size: str
    risk_score: int
    risk: str
    status: str
    priority: int
    location: str
    description: str
    connected_assets: List[NodeRelationship] = Field(default_factory=list)
    incoming_relationships: List[NodeRelationship] = Field(default_factory=list)
    outgoing_relationships: List[NodeRelationship] = Field(default_factory=list)
    certificates: List[Dict[str, str]] = Field(default_factory=list)
    dependencies: List[Dict[str, str]] = Field(default_factory=list)
    explainability_summary: Dict[str, Any] = Field(default_factory=dict)
    migration_recommendation: Dict[str, Any] = Field(default_factory=dict)
    graph_metrics: Dict[str, float] = Field(default_factory=dict)
