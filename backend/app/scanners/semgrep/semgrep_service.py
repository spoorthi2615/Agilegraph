import logging
from typing import List

from app.scanners.semgrep.finding_normalizer import FindingNormalizer
from app.scanners.semgrep.semgrep_finding import SemgrepFinding
from app.scanners.semgrep.semgrep_parser import SemgrepParser
from app.scanners.semgrep.semgrep_runner import SemgrepRunner

logger = logging.getLogger(__name__)


class SemgrepService:
    """
    Facade orchestrator for the Semgrep integration layer.
    Utilizes strict Dependency Injection to remain decoupled from concrete implementations.
    """

    def __init__(self, runner: SemgrepRunner, parser: SemgrepParser, normalizer: FindingNormalizer):
        self.runner = runner
        self.parser = parser
        self.normalizer = normalizer

    def scan_and_merge(
        self, target_directory: str, existing_findings: List[SemgrepFinding]
    ) -> List[SemgrepFinding]:
        """
        Executes Semgrep, parses the output from file I/O, and merges it immutably with existing findings.
        Returns a strongly typed list directly mapping into Graph Nodes.
        """
        logger.info(f"Initiating Semgrep scan on {target_directory}...")

        # Runner now securely writes to a temporary JSON file to prevent RAM OOM crashes
        temp_file_path = self.runner.execute(target_directory)

        if not temp_file_path:
            logger.warning(
                "Semgrep execution failed or returned no data. Proceeding with existing findings only."
            )
            return [f.model_copy() for f in existing_findings]

        # Parser natively reads the file and deletes it to clean up the environment
        findings = self.parser.parse_file(temp_file_path)
        logger.info(f"Semgrep returned {len(findings)} raw findings. Normalizing...")

        # Normalization preserves immutable inputs and protects duplicate finding vulnerabilities
        merged = self.normalizer.normalize(existing_findings, findings)
        logger.info(f"Normalization complete. Total merged findings: {len(merged)}")
        return merged
