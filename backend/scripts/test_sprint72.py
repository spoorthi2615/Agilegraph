import os
import sys
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.live_tls.tls_config import TLSConfig
from app.scanners.live_tls.tls_connection import TLSConnectionManager
from app.scanners.live_tls.tls_scanner import TLSScanner
from app.scanners.live_tls.tls_service import TLSService
from app.scanners.live_tls.tls_finding import TLSFinding
from app.scanners.live_tls.tls_certificate import TLSCertificate

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint72():
    logging.info("Testing Sprint 71 Post-Review Architecture Fixes...")
    
    config = TLSConfig(timeout_seconds=5)
    
    # 1. Dependency Inversion Verification
    conn_manager = TLSConnectionManager(config)
    scanner = TLSScanner()
    service = TLSService(conn_manager, scanner)
    
    # 2. Immutability Verification (Risk Analyzer)
    now = datetime.now(timezone.utc)
    mock_cert = TLSCertificate(
        subject="CN=mock.expired.com",
        issuer="CN=mock.expired.com",
        serial_number="12345",
        valid_from=(now - timedelta(days=100)).isoformat(),
        valid_until=(now - timedelta(days=5)).isoformat(),
        signature_algorithm="sha1WithRSAEncryption",
        public_key_algorithm="RSA",
        key_length=1024,
        common_name="mock.expired.com"
    )
    
    base_finding = TLSFinding(
        domain="mock.expired.com",
        port=443,
        tls_version="TLSv1",
        cipher_suite="TLS_RSA_WITH_RC4_128_MD5",
        certificate=mock_cert
    )
    
    enriched_finding = service.scanner.analyze_risk(base_finding)
    
    assert base_finding.risk_score == 0.0, "Immutability violated! Base object mutated."
    assert enriched_finding.risk_score == 10.0, "Risk analyzer failed to flag critical flaws."
    logging.info("Risk Detection is functionally pure and immutable.")
    
    # 3. Security (SSRF Verification)
    with patch('socket.gethostbyname') as mock_dns:
        # Simulate local network resolution
        mock_dns.return_value = "127.0.0.1"
        result = conn_manager.get_live_connection_data("internal-admin.local", 443)
        assert result == (None, None), "SSRF logic failed to block loopback request!"
        
        mock_dns.return_value = "169.254.169.254"
        result = conn_manager.get_live_connection_data("aws-metadata", 80)
        assert result == (None, None), "SSRF logic failed to block AWS metadata request!"
        
    logging.info("Network SSRF Anti-Scanning Firewall passed.")
    
    # 4. Graph Mapping Translater
    edges = enriched_finding.to_graph_edges()
    assert ("Domain:mock.expired.com", "USES_PROTOCOL", "Protocol:TLSv1") in edges
    assert ("Domain:mock.expired.com", "SECURED_BY", "Certificate:12345") in edges
    assert ("Certificate:12345", "ISSUED_BY", "CA:CN=mock.expired.com") in edges
    logging.info("Graph Edge Translation Logic passed.")
    
    logging.info("All Sprint 71 Post-Review Architecture fixes passed successfully!")

if __name__ == "__main__":
    test_sprint72()
