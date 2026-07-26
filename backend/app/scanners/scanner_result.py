from typing import List, Dict, Any
from pydantic import BaseModel

class ScannerResult(BaseModel):
    """
    Standardized output model for all scanners in the AgileGraph framework.
    """
    scanner_name: str
    status: str
    findings: List[Dict[str, Any]]
    errors: List[str]
    execution_time_ms: float
    metadata: Dict[str, Any]
