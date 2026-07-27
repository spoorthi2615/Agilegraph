from pydantic import BaseModel, Field
from typing import List, Optional

class KPISummary(BaseModel):
    totalAssets: int = Field(default=0)
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    migrationProgress: int = Field(default=0)
    pqcReadiness: int = Field(default=0)
    lastScan: str = Field(default="N/A")

class RiskDistribution(BaseModel):
    name: str
    value: int
    color: str

class AlgorithmUsage(BaseModel):
    algorithm: str
    count: int

class DepartmentUsage(BaseModel):
    department: str
    assets: int
    critical: int

class MigrationTrend(BaseModel):
    month: str
    migrated: int
    planned: int

class ScanRecord(BaseModel):
    id: str
    name: str
    source: str
    startedAt: str
    duration: str
    assets: int
    criticalFindings: int
    status: str

class ActivityItem(BaseModel):
    id: str
    actor: str
    action: str
    target: str
    time: str
    kind: str

class CriticalAlert(BaseModel):
    id: str
    title: str
    reason: str
    score: int

class DashboardSummary(BaseModel):
    kpis: KPISummary = Field(default_factory=KPISummary)
    riskDistribution: List[RiskDistribution] = Field(default_factory=list)
    algorithmUsage: List[AlgorithmUsage] = Field(default_factory=list)
    departmentUsage: List[DepartmentUsage] = Field(default_factory=list)
    migrationTrend: List[MigrationTrend] = Field(default_factory=list)
    recentScans: List[ScanRecord] = Field(default_factory=list)
    activity: List[ActivityItem] = Field(default_factory=list)
    criticalAlerts: List[CriticalAlert] = Field(default_factory=list)

class DashboardNode(BaseModel):
    id: str
    label: str
    type: str
    risk: str
    x: float
    y: float

class DashboardEdge(BaseModel):
    source: str
    target: str

class DashboardGraph(BaseModel):
    nodes: List[DashboardNode] = Field(default_factory=list)
    edges: List[DashboardEdge] = Field(default_factory=list)

class ReportRecord(BaseModel):
    id: str
    title: str
    type: str
    createdAt: str
    size: str
    author: str
