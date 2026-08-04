from pydantic import BaseModel
from typing import List, Optional

class DomainScanRequest(BaseModel):
    domain: str
    ports: List[int] = [443]

class ScanResponse(BaseModel):
    project_id: str
    status: str
    message: Optional[str] = None
