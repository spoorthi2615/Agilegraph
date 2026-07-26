import logging
from typing import List, Dict, Any
from app.scanners.semgrep.semgrep_config import SemgrepConfig
from app.scanners.semgrep.semgrep_runner import SemgrepRunner
from app.scanners.semgrep.semgrep_parser import SemgrepParser
from app.scanners.semgrep.finding_normalizer import FindingNormalizer

logger = logging.getLogger(__name__)

class SemgrepService:
    """
    Facade orchestrator for the entire Semgrep integration layer.
    """
    def __init__(self, config: SemgrepConfig):
        self.config = config
        self.runner = SemgrepRunner(config)
        
    def scan_and_merge(self, target_directory: str, existing_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes Semgrep, parses the output, merges it with existing findings, and returns the unified list.
        """
        logger.info(f"Initiating Semgrep scan on {target_directory}...")
        raw_json = self.runner.execute(target_directory)
        
        if raw_json is None:
            logger.warning("Semgrep execution failed or returned no data. Proceeding with existing findings only.")
            # Ensure existing findings have attribution
            for f in existing_findings:
                if "source" not in f:
                    f["source"] = "Custom"
            return existing_findings
            
        findings = SemgrepParser.parse(raw_json)
        logger.info(f"Semgrep returned {len(findings)} raw findings. Normalizing...")
        
        merged = FindingNormalizer.normalize(existing_findings, findings)
        logger.info(f"Normalization complete. Total merged findings: {len(merged)}")
        return merged
