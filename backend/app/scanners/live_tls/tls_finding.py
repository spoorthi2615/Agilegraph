from datetime import datetime, timezone
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from app.scanners.live_tls.tls_certificate import TLSCertificate


class TLSFinding(BaseModel):
    """
    Resulting container mapping a target domain to its live TLS environment.
    """

    domain: str
    port: int

    tls_version: str
    cipher_suite: str
    alpn: Optional[str] = None
    key_exchange: Optional[str] = None
    certificate_chain_length: int = Field(default=0)

    certificate: Optional[TLSCertificate] = None

    risk_score: float = Field(default=0.0)
    findings: List[str] = Field(default_factory=list)

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_graph_edges(self) -> List[Tuple[str, str, str]]:
        """
        Deterministically translates this data structure into Graph Database Edges.
        Format: (SourceNode, RELATIONSHIP, TargetNode)
        """
        edges = []
        domain_node = f"Domain:{self.domain}"

        # Protocol Edges
        edges.append((domain_node, "USES_PROTOCOL", f"Protocol:{self.tls_version}"))
        edges.append((domain_node, "USES_CIPHER", f"CipherSuite:{self.cipher_suite}"))

        if self.certificate:
            cert_node = f"Certificate:{self.certificate.serial_number}"
            edges.append((domain_node, "SECURED_BY", cert_node))
            edges.append((cert_node, "ISSUED_BY", f"CA:{self.certificate.issuer}"))
            edges.append(
                (cert_node, "USES_ALGORITHM", f"Algorithm:{self.certificate.public_key_algorithm}")
            )
            edges.append(
                (cert_node, "SIGNED_WITH", f"Signature:{self.certificate.signature_algorithm}")
            )

        return edges
