from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class DashboardBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class KPISummary(DashboardBaseModel):
    total_assets: int = Field(default=0)
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    migration_progress: int = Field(default=0)
    pqc_readiness: int = Field(default=0)
    last_scan: str = Field(default="N/A")

class RiskDistribution(DashboardBaseModel):
    name: str
    value: int
    color: str

class AlgorithmUsage(DashboardBaseModel):
    algorithm: str
    count: int

class DepartmentUsage(DashboardBaseModel):
    department: str
    assets: int
    critical: int

class MigrationTrend(DashboardBaseModel):
    month: str
    migrated: int
    planned: int

class ScanRecord(DashboardBaseModel):
    id: str
    name: str
    source: str
    started_at: str
    duration: str
    assets: int
    critical_findings: int
    status: str
    owner_email: Optional[str] = None

class ActivityItem(DashboardBaseModel):
    id: str
    actor: str
    action: str
    target: str
    time: str
    kind: str

class CriticalAlert(DashboardBaseModel):
    id: str
    title: str
    reason: str
    score: int
    owner_email: Optional[str] = None

class DashboardSummary(DashboardBaseModel):
    kpis: KPISummary = Field(default_factory=KPISummary)
    risk_distribution: List[RiskDistribution] = Field(default_factory=list)
    algorithm_usage: List[AlgorithmUsage] = Field(default_factory=list)
    department_usage: List[DepartmentUsage] = Field(default_factory=list)
    migration_trend: List[MigrationTrend] = Field(default_factory=list)
    recent_scans: List[ScanRecord] = Field(default_factory=list)
    activity: List[ActivityItem] = Field(default_factory=list)
    critical_alerts: List[CriticalAlert] = Field(default_factory=list)

class DashboardNode(DashboardBaseModel):
    id: str
    label: str
    type: str
    risk: str
    x: float
    y: float

class DashboardEdge(DashboardBaseModel):
    source: str
    target: str

class DashboardGraph(DashboardBaseModel):
    nodes: List[DashboardNode] = Field(default_factory=list)
    edges: List[DashboardEdge] = Field(default_factory=list)

class ReportRecord(DashboardBaseModel):
    id: str
    title: str
    type: str
    created_at: str
    size: str
    author: str
