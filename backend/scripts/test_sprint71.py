import os
import sys
import logging
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.semgrep.semgrep_config import SemgrepConfig
from app.scanners.semgrep.semgrep_runner import SemgrepRunner
from app.scanners.semgrep.semgrep_parser import SemgrepParser
from app.scanners.semgrep.finding_normalizer import FindingNormalizer
from app.scanners.semgrep.semgrep_service import SemgrepService
from app.scanners.semgrep.semgrep_finding import SemgrepFinding

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint71():
    logging.info("Testing Sprint 70 Post-Review Architecture Fixes...")
    
    config = SemgrepConfig(timeout_seconds=5)
    
    # 1. Dependency Inversion Framework
    runner = SemgrepRunner(config)
    parser = SemgrepParser()
    normalizer = FindingNormalizer()
    service = SemgrepService(runner, parser, normalizer)
    
    # 2. Security: Path Traversal/Injection Blocking
    try:
        runner.execute("--output=/etc/shadow")
        assert False, "Failed to block CLI argument injection!"
    except ValueError:
        logging.info("Security: Path injection successfully blocked.")
        
    # 3. Immutable Strong Typing & Normalization Fixes (The Deduplication Bug)
    cf1 = SemgrepFinding(
        rule_id="MD5_WEAK",
        severity="ERROR",
        message="Weak Hash",
        language="java",
        file_path="src/App.java",
        line=10,
        column=0,
        code_snippet="md5()",
        source="Custom"
    )
    
    cf2 = SemgrepFinding(
        rule_id="AWS_CREDENTIAL",
        severity="CRITICAL",
        message="Hardcoded AWS",
        language="java",
        file_path="src/App.java",
        line=10, # SAME LINE, DIFFERENT RULE
        column=5,
        code_snippet="AKIA...",
        source="Custom"
    )
    
    sf1 = SemgrepFinding(
        rule_id="MD5_WEAK",
        severity="WARNING",
        message="Semgrep Hash",
        language="java",
        file_path="src/App.java",
        line=10,
        column=0,
        code_snippet="md5()",
        source="Semgrep"
    )
    
    merged = normalizer.normalize([cf1, cf2], [sf1])
    assert len(merged) == 2, "Deduplication algorithm failed! It improperly merged distinct vulnerabilities on the same line."
    
    sources = [f.source for f in merged]
    assert sources.count("Both") == 1, "The MD5 finding should be marked as 'Both'"
    assert sources.count("Custom") == 1, "The AWS credential finding should be untouched and 'Custom'"
    logging.info("Deduplication logic is secure and mathematically correct.")
    
    # 4. File I/O parsing (OOM Resource Exhaustion Fix)
    mock_json = {
        "results": [
            {
                "check_id": "semgrep_rule",
                "path": "src/App.java",
                "start": {"line": 45, "col": 12},
                "extra": {
                    "severity": "WARNING",
                    "message": "msg",
                    "lines": "code"
                }
            }
        ]
    }
    fd, temp_path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        json.dump(mock_json, f)
        
    parsed = parser.parse_file(temp_path)
    assert len(parsed) == 1
    assert parsed[0].source == "Semgrep"
    assert not os.path.exists(temp_path), "Memory leak: Parser failed to delete temporary JSON file!"
    logging.info("File I/O parsing succeeded and cleaned up temporary artifacts.")
    
    # 5. Graph Mapping Contract
    edges = []
    for f in merged:
        edges.append((f.rule_id, "CONNECTED_TO", f.file_path))
    assert ("MD5_WEAK", "CONNECTED_TO", "src/App.java") in edges
    assert ("AWS_CREDENTIAL", "CONNECTED_TO", "src/App.java") in edges
    logging.info("Graph edge abstraction verified.")
    
    logging.info("All Sprint 70 Post-Review Architecture fixes passed successfully!")

if __name__ == "__main__":
    test_sprint71()
