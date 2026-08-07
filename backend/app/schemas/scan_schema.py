from typing import List, Optional

from pydantic import BaseModel


class DomainScanRequest(BaseModel):
    domain: str
    ports: List[int] = [443]


class ScanResponse(BaseModel):
    project_id: str
    status: str
    message: Optional[str] = None
