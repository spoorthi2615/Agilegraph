import os
import sys
import logging
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.certificate_transparency.ct_config import CTConfig
from app.scanners.certificate_transparency.ct_client import CTClient
from app.scanners.certificate_transparency.ct_parser import CTParser
from app.scanners.certificate_transparency.ct_service import CTService
from app.scanners.certificate_transparency.ct_finding import CTFinding

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint73():
    logging.info("Testing Sprint 72 Certificate Transparency OSINT Framework...")
    
    config = CTConfig(timeout_seconds=2, max_retries=1)
    
    # 1. Dependency Inversion Verification
    client = CTClient(config)
    parser = CTParser()
    service = CTService(client, parser)
    
    now = datetime.now(timezone.utc)
    mock_json = [
        {
            "id": 10001,
            "issuer_name": "C=US, O=Let's Encrypt, CN=R3",
            "name_value": "example.com\nwww.example.com",
            "common_name": "example.com",
            "serial_number": "040000000000000000000000000000000000",
            "not_before": (now - timedelta(days=50)).isoformat(),
            "not_after": (now + timedelta(days=40)).isoformat()
        },
        {
            "id": 10002, # Exact same serial, logged to a different transparency server
            "issuer_name": "C=US, O=Let's Encrypt, CN=R3",
            "name_value": "example.com\nwww.example.com",
            "common_name": "example.com",
            "serial_number": "040000000000000000000000000000000000",
            "not_before": (now - timedelta(days=50)).isoformat(),
            "not_after": (now + timedelta(days=40)).isoformat()
        },
        {
            "id": 10003, # Expired cert
            "issuer_name": "C=US, O=DigiCert, CN=DigiCert CA",
            "name_value": "example.com",
            "common_name": "example.com",
            "serial_number": "0A1B2C",
            "not_before": (now - timedelta(days=800)).isoformat(),
            "not_after": (now - timedelta(days=400)).isoformat()
        }
    ]
    
    # Mocking the urllib response
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(mock_json).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        findings = service.scan_domain("example.com")
        
        # 2. Verify Deduplication
        assert len(findings) == 2, "Deduplication failed! Identical serial numbers from multiple CT logs were not merged."
        logging.info("Deduplication successfully collapsed redundant log entries.")
        
        # 3. Verify Risk Analyzer & Immutability
        active_cert = next(f for f in findings if f.serial_number == "040000000000000000000000000000000000")
        expired_cert = next(f for f in findings if f.serial_number == "0A1B2C")
        
        assert "Active Certificate" in active_cert.findings
        assert "Historically Expired Certificate" in expired_cert.findings
        logging.info("Risk analyzer correctly distinguished active from expired historical certificates.")
        
        # 4. Verify SAN Parsing
        assert len(active_cert.san_entries) == 2, "SAN entries not parsed from name_value newlines correctly."
        assert "www.example.com" in active_cert.san_entries
        
        # 5. Graph Translation Logic
        edges = expired_cert.to_graph_edges()
        assert ("TransparencyLog:crt.sh", "LOGS", "Certificate:0A1B2C") in edges
        assert ("Certificate:0A1B2C", "SECURES", "Domain:example.com") in edges
        logging.info("Graph Database serialization mappings passed.")
        
    logging.info("All Sprint 72 CT tests passed successfully!")

if __name__ == "__main__":
    test_sprint73()
