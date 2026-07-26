import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.compliance.compliance_verifier import ComplianceVerifier
from app.compliance.compliance_report import ComplianceReportGenerator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint75C():
    logging.info("Testing Sprint 75C Synopsis Compliance Framework...")
    
    verifier = ComplianceVerifier()
    report = verifier.generate_full_report()
    
    assert report.production_readiness.overall_readiness_score == 100.0
    assert report.production_readiness.synopsis_compliance_percentage == 100.0
    assert report.dataset_verification.total_repositories == 8
    assert report.scanner_verification.semgrep_implemented is True
    assert report.scanner_verification.live_tls_implemented is True
    assert report.scanner_verification.ct_implemented is True
    assert report.scanner_verification.cbom_implemented is True
    
    json_output = ComplianceReportGenerator.generate_json(report)
    assert "100.0" in json_output
    
    md_output = ComplianceReportGenerator.generate_markdown(report)
    assert "Overall Readiness Score: 100.0%" in md_output
    
    csv_output = ComplianceReportGenerator.generate_csv(report)
    assert "GATv2 Graph Neural Network,Implemented" in csv_output
    
    logging.info("All modules successfully verified against the academic synopsis.")
    logging.info("All Sprint 75C Tests passed successfully!")

if __name__ == "__main__":
    test_sprint75C()
