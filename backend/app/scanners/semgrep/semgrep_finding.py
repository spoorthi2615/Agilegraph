from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SemgrepFinding(BaseModel):
    """
    Strongly typed representation of a Semgrep vulnerability finding.
    """

    rule_id: str
    severity: str
    message: str
    language: str
    file_path: str
    line: int
    column: int
    code_snippet: str

    # Attribution
    source: str = Field(default="Semgrep")
    semgrep_rule_id: Optional[str] = None

    # Metadata for CWE/OWASP mapping and Graph integration
    metadata: Dict[str, Any] = Field(default_factory=dict)
