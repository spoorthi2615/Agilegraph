from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from pathlib import Path
from pydantic import BaseModel, Field

class AssetType(str, Enum):
    """
    Enumeration of recognized cryptographic asset classifications.
    """
    KEY = "KEY"
    CERTIFICATE = "CERTIFICATE"
    HASH = "HASH"
    SYMMETRIC_KEY = "SYMMETRIC_KEY"
    ASYMMETRIC_KEY = "ASYMMETRIC_KEY"
    DEPENDENCY = "DEPENDENCY"
    JWT = "JWT"
    UNKNOWN = "UNKNOWN"

class Severity(str, Enum):
    """
    Enumeration of risk severity levels associated with a cryptographic asset.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CryptoAsset(BaseModel):
    """
    Core domain model representing a single cryptographic asset discovered during analysis.
    """
    asset_id: UUID = Field(default_factory=uuid4)
    asset_type: AssetType
    algorithm: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    severity: Optional[Severity] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
