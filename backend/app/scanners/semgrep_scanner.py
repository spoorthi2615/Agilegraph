import time
from pathlib import Path
from typing import List

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType
from app.scanners.semgrep.semgrep_runner import SemgrepRunner
from app.scanners.semgrep.semgrep_parser import SemgrepParser
from app.scanners.semgrep.finding_normalizer import FindingNormalizer
from app.scanners.semgrep.semgrep_service import SemgrepService

class SemgrepScanner(BaseScanner):
    """
    Scanner implementation that runs Semgrep against the codebase.
    Uses the existing SemgrepService to extract and normalize findings.
    """
    @property
    def name(self) -> str:
        return "SemgrepScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        # Semgrep supports many languages, but we primarily target these
        return ["Python", "Java", "Go"]
        
    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        
        # Build config: use lightweight named rules (p/secrets, p/python) — no full registry download
        from app.scanners.semgrep.semgrep_config import SemgrepConfig
        config = SemgrepConfig(use_default_rules=True, timeout_seconds=120)
        
        # Instantiate dependencies for the service
        runner = SemgrepRunner(config)
        parser = SemgrepParser()
        normalizer = FindingNormalizer()
        
        service = SemgrepService(runner, parser, normalizer)
        
        # Execute Semgrep
        semgrep_findings = service.scan_and_merge(str(project_path.absolute()), [])
        
        # Map SemgrepFindings to CryptoAssets for the ScannerResult
        mapped_findings = []
        for sf in semgrep_findings:
            asset = CryptoAsset(
                asset_type=AssetType.CODE_SNIPPET,
                algorithm=sf.rule_id.split(".")[-1], # Rough extraction of algo from rule ID
                language="Unknown", # Could be inferred from file extension
                file_path=Path(sf.file_path),
                line_number=sf.line_number,
                severity=sf.severity,
                confidence=1.0, # Semgrep rules are high confidence static analysis
                metadata={
                    "rule_id": sf.rule_id,
                    "message": sf.message,
                    "match_snippet": sf.match_snippet
                }
            )
            mapped_findings.append(asset.model_dump(mode="json"))
            
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success",
            findings=mapped_findings,
            errors=[], # SemgrepService handles internal errors and logging
            execution_time_ms=execution_time_ms,
            metadata={"total_semgrep_findings": len(mapped_findings)}
        )
