from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLabel(str, Enum):
    """
    The standardized labels for Cryptographic Risk.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ExpertLabel(BaseModel):
    """
    A single assessment cast by a specific expert on a specific asset.
    """

    asset_id: str
    expert_id: str
    label: RiskLabel
    confidence: int = Field(ge=1, le=100)
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
