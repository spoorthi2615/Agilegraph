import os
import sys
import logging
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.semgrep.semgrep_config import SemgrepConfig
from app.scanners.semgrep.semgrep_service import SemgrepService
from app.scanners.semgrep.finding_normalizer import FindingNormalizer
from app.scanners.semgrep.semgrep_finding import SemgrepFinding
from app.scanners.semgrep.semgrep_parser import SemgrepParser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint71():
    logging.info("Testing Sprint 70/71 Semgrep Integration Layer...")
    
    config = SemgrepConfig(timeout_seconds=5)
    service = SemgrepService(config)
    
    # 1. JSON Parsing & Language Resolution Test
    mock_json = {
        "results": [
            {
                "check_id": "java.lang.security.audit.crypto",
                "path": "src/main/java/App.java",
                "start": {"line": 45, "col": 12},
                "extra": {
                    "severity": "WARNING",
                    "message": "Weak cryptographic algorithm detected.",
                    "lines": "MessageDigest.getInstance(\"MD5\");"
                }
            }
        ]
    }
    
    parsed_findings = SemgrepParser.parse(mock_json)
    assert len(parsed_findings) == 1
    assert parsed_findings[0].language == "java", "Failed to resolve language from file extension!"
    assert parsed_findings[0].rule_id == "java.lang.security.audit.crypto"
    assert parsed_findings[0].line == 45
    logging.info("JSON Parsing & Language Mapping Test passed.")
    
    # 2. Normalization / Deduplication Test
    custom_findings = [
        {"file_path": "src/main/java/App.java", "line": 45, "rule_id": "AG_MD5_WEAK"}
    ]
    
    merged = FindingNormalizer.normalize(custom_findings, parsed_findings)
    assert len(merged) == 1, "Failed to deduplicate overlapping findings!"
    assert merged[0]["source"] == "Both", "Failed to update attribution source to 'Both'"
    assert merged[0]["semgrep_rule_id"] == "java.lang.security.audit.crypto"
    logging.info("Normalization & Deduplication Test passed.")
    
    # 3. Disjoint Findings Merge Test
    disjoint_custom = [
        {"file_path": "src/main/java/App.java", "line": 10, "rule_id": "AG_SHA1_WEAK"}
    ]
    merged_disjoint = FindingNormalizer.normalize(disjoint_custom, parsed_findings)
    assert len(merged_disjoint) == 2, "Failed to natively merge disjoint findings!"
    
    sources = [f["source"] for f in merged_disjoint]
    assert "Custom" in sources and "Semgrep" in sources, "Attribution lost during merge!"
    logging.info("Disjoint Merging Test passed.")
    
    # 4. Graceful Degradation Test (CLI Missing)
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result_degraded = service.scan_and_merge(".", disjoint_custom)
        assert len(result_degraded) == 1, "Failed to gracefully degrade when CLI is missing!"
        assert result_degraded[0]["source"] == "Custom", "Attribution failed on fallback!"
        
    logging.info("Graceful Degradation (Missing CLI) Test passed.")
    logging.info("All Sprint 71 Semgrep Integration tests passed successfully!")

if __name__ == "__main__":
    test_sprint71()
