import os
import sys
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.live_tls.tls_config import TLSConfig
from app.scanners.live_tls.tls_service import TLSService
from app.scanners.live_tls.tls_finding import TLSFinding
from app.scanners.live_tls.tls_certificate import TLSCertificate

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint72():
    logging.info("Testing Sprint 71/72 Live TLS Scanning Framework...")
    
    config = TLSConfig(timeout_seconds=5)
    service = TLSService(config)
    
    # 1. Test Risk Detection Logic (Security Triggers)
    now = datetime.now(timezone.utc)
    expired_date = (now - timedelta(days=5)).isoformat()
    
    mock_cert = TLSCertificate(
        subject="CN=mock.expired.com",
        issuer="CN=mock.expired.com", # Self-signed
        serial_number="12345",
        valid_from=(now - timedelta(days=100)).isoformat(),
        valid_until=expired_date,
        signature_algorithm="sha1WithRSAEncryption", # Weak sig
        public_key_algorithm="RSA",
        key_length=1024, # Weak key
        common_name="mock.expired.com"
    )
    
    finding = TLSFinding(
        domain="mock.expired.com",
        port=443,
        tls_version="TLSv1", # Weak protocol
        cipher_suite="TLS_RSA_WITH_RC4_128_MD5", # Weak cipher
        certificate=mock_cert
    )
    
    service.scanner.analyze_risk(finding)
    
    assert finding.risk_score == 10.0, f"Score should cap at 10.0, got {finding.risk_score}"
    assert any("Unsupported/Deprecated Protocol" in f for f in finding.findings)
    assert any("Weak Cipher Suite" in f for f in finding.findings)
    assert any("Expired certificate" in f for f in finding.findings)
    assert any("Weak signature algorithm" in f for f in finding.findings)
    assert any("Weak RSA key" in f for f in finding.findings)
    assert any("Self-signed" in f for f in finding.findings)
    
    logging.info("Risk Detection logic passed all security triggers.")
    
    # 2. Test Graceful Network Timeout Isolation
    with patch('socket.create_connection') as mock_sock:
        import socket
        mock_sock.side_effect = socket.timeout()
        
        result = service.scan_domain("unreachable.timeout.test")
        assert result is None, "Service should gracefully return None on socket timeout"
        
    logging.info("Network Timeout isolation passed.")
    
    # 3. Simulated Successful Live Socket Parsing
    with patch('app.scanners.live_tls.tls_connection.TLSConnectionManager.get_live_connection_data') as mock_conn:
        mock_sock = MagicMock()
        mock_sock.version.return_value = "TLSv1.3"
        mock_sock.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
        mock_sock.selected_alpn_protocol.return_value = "h2"
        
        mock_conn.return_value = (None, mock_sock)
        
        result_live = service.scan_domain("google.com")
        
        assert result_live is not None
        assert result_live.domain == "google.com"
        assert result_live.tls_version == "TLSv1.3"
        assert result_live.cipher_suite == "TLS_AES_256_GCM_SHA384"
        assert result_live.alpn == "h2"
        assert result_live.risk_score == 0.0 # Clean cert/protocol defaults to 0.0
        
    logging.info("Live Orchestration graph mapping passed.")
    logging.info("All Sprint 71 Live TLS scanner tests passed successfully!")

if __name__ == "__main__":
    test_sprint72()
