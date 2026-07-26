import logging
from typing import Optional
from app.scanners.live_tls.tls_config import TLSConfig
from app.scanners.live_tls.tls_connection import TLSConnectionManager
from app.scanners.live_tls.tls_scanner import TLSScanner
from app.scanners.live_tls.tls_finding import TLSFinding

logger = logging.getLogger(__name__)

class TLSService:
    """
    Facade orchestrating the live TLS network connection, certificate extraction, and risk analysis.
    """
    def __init__(self, config: TLSConfig):
        self.config = config
        self.connection_manager = TLSConnectionManager(config)
        self.scanner = TLSScanner()
        
    def scan_domain(self, domain: str, port: Optional[int] = None) -> Optional[TLSFinding]:
        """
        Executes a live network scan against the target domain.
        Returns a populated TLSFinding object, ready for Graph Integration.
        """
        target_port = port if port else self.config.default_port
        
        der_bytes, ssock = self.connection_manager.get_live_connection_data(domain, target_port)
        
        if not ssock:
            return None
            
        # Extract TLS Protocol metadata from the active socket
        tls_version = ssock.version() or "UNKNOWN"
        cipher_suite = ssock.cipher()
        cipher_name = cipher_suite[0] if cipher_suite else "UNKNOWN"
        alpn = ssock.selected_alpn_protocol()
        
        # Initialize the Graph Node mapping model
        finding = TLSFinding(
            domain=domain,
            port=target_port,
            tls_version=tls_version,
            cipher_suite=cipher_name,
            alpn=alpn
        )
        
        if der_bytes:
            cert_model = self.scanner.parse_der_certificate(der_bytes)
            if cert_model:
                finding.certificate = cert_model
                finding.certificate_chain_length = 1
                
        # Run Risk Detection (evaluates key length, signatures, dates, etc.)
        self.scanner.analyze_risk(finding)
        
        # Close the socket cleanly
        try:
            ssock.close()
        except Exception:
            pass
            
        return finding
