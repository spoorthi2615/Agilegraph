from typing import List, Optional

from pydantic import BaseModel, Field


class SemgrepConfig(BaseModel):
    """
    Configuration for the Semgrep CLI execution and orchestration.
    """

    custom_rules_dir: Optional[str] = Field(default=None)
    use_default_rules: bool = Field(default=True)
    language_filters: List[str] = Field(default_factory=list)
    exclude_dirs: List[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=300)
