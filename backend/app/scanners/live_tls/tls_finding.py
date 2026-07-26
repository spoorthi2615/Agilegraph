from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from app.scanners.live_tls.tls_certificate import TLSCertificate

class TLSFinding(BaseModel):
    """
    Resulting container mapping a target domain to its live TLS environment.
    """
    domain: str
    port: int
    
    # TLS Protocol metadata
    tls_version: str
    cipher_suite: str
    alpn: Optional[str] = None
    key_exchange: Optional[str] = None
    certificate_chain_length: int = Field(default=0)
    
    certificate: Optional[TLSCertificate] = None
    
    # Analyzed Risk Metadata
    risk_score: float = Field(default=0.0)
    findings: List[str] = Field(default_factory=list)
    
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
