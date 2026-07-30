from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime, timezone

class CTFinding(BaseModel):
    """
    Strongly typed representation of a historical certificate retrieved from a transparency log.
    """
    domain: str
    certificate_id: int
    issuer: str
    subject: str
    common_name: str
    san_entries: List[str] = Field(default_factory=list)
    serial_number: str
    not_before: str
    not_after: str
    signature_algorithm: str = Field(default="UNKNOWN")
    certificate_hash: Optional[str] = None
    
    logged_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_score: float = Field(default=0.0)
    findings: List[str] = Field(default_factory=list)
    
    def to_graph_edges(self) -> List[Tuple[str, str, str]]:
        """
        Deterministically translates this data structure into Graph Database Edges.
        Format: (SourceNode, RELATIONSHIP, TargetNode)
        """
        edges = []
        domain_node = f"Domain:{self.domain}"
        cert_node = f"Certificate:{self.serial_number}"
        log_node = "TransparencyLog:crt.sh"
        ca_node = f"CA:{self.issuer}"
        
        edges.append((log_node, "LOGS", cert_node))
        edges.append((cert_node, "SECURES", domain_node))
        edges.append((cert_node, "ISSUED_BY", ca_node))
        
        if self.signature_algorithm != "UNKNOWN":
            edges.append((cert_node, "SIGNED_WITH", f"Algorithm:{self.signature_algorithm}"))
            
        return edges
