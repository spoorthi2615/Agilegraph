from pydantic import BaseModel, Field
from typing import List, Optional

class TLSCertificate(BaseModel):
    """
    Strongly typed representation of an X.509 Certificate pulled from a live TLS handshake.
    """
    subject: str
    issuer: str
    serial_number: str
    valid_from: str
    valid_until: str
    signature_algorithm: str
    
    public_key_algorithm: str = Field(default="UNKNOWN")
    key_length: int = Field(default=0)
    san_entries: List[str] = Field(default_factory=list)
    common_name: str
    fingerprint: Optional[str] = None
