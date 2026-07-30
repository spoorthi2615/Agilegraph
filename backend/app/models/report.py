from pydantic import BaseModel, Field, ConfigDict
from typing import List
from enum import Enum

def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

class ReportBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

class ReportCategory(str, Enum):
    DASHBOARD = "Dashboard"
    GRAPH = "Graph"
    EXPLAINABILITY = "Explainability"
    BENCHMARK = "Benchmark"
    EVALUATION = "Evaluation"
    MIGRATION = "Migration"
    COMPLIANCE = "Compliance"
    VALIDATION = "Validation"
    WORKFLOW = "Workflow"

class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"

class ReportMetadata(ReportBaseModel):
    generated_at: str = Field(default="")
    version: str = Field(default="1.0")
    generator: str = Field(default="AgileGraph")
    repository: str = Field(default="unknown")
    status: str = Field(default="completed")
    checksum: str = Field(default="")

class ReportStatistics(ReportBaseModel):
    total_findings: int = Field(default=0)
    critical_findings: int = Field(default=0)
    high_findings: int = Field(default=0)

class DownloadLink(ReportBaseModel):
    format: str
    url: str

class ReportSummary(ReportBaseModel):
    id: str
    title: str
    category: str
    description: str = Field(default="")
    format: str = Field(default="markdown")
    created_at: str = Field(default="")
    generated_by: str = Field(default="System")
    file_size: str = Field(default="0 KB")
    status: str = Field(default="available")
    download_availability: bool = Field(default=True)

class ReportPreview(ReportBaseModel):
    preview_content: str = Field(default="")
    is_truncated: bool = Field(default=True)

class ReportDetail(ReportSummary):
    metadata: ReportMetadata = Field(default_factory=ReportMetadata)
    statistics: ReportStatistics = Field(default_factory=ReportStatistics)
    available_formats: List[str] = Field(default_factory=list)
    preview: ReportPreview = Field(default_factory=ReportPreview)
    download_links: List[DownloadLink] = Field(default_factory=list)

class PaginatedReportResponse(ReportBaseModel):
    items: List[ReportSummary] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    size: int = Field(default=20)
    total_pages: int = Field(default=1)
