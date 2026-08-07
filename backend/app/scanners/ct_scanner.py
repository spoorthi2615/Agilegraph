import json
import logging
import time
from pathlib import Path
from typing import List

from app.models.crypto_asset import AssetType, CryptoAsset
from app.scanners.base_scanner import BaseScanner
from app.scanners.certificate_transparency.ct_client import CTClient
from app.scanners.certificate_transparency.ct_parser import CTParser
from app.scanners.certificate_transparency.ct_service import CTService
from app.scanners.scanner_result import ScannerResult

logger = logging.getLogger(__name__)


class CTScanner(BaseScanner):
    """
    Scanner implementation that runs Certificate Transparency log checks against
    domains explicitly provided in the project's .agilegraph config file.
    """

    @property
    def name(self) -> str:
        return "CertificateTransparencyScanner"

    @property
    def supported_languages(self) -> List[str]:
        return ["All"]  # Infrastructure/Domain level scan

    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        findings = []
        errors = []

        # Look for .agilegraph or agilegraph.json to extract domains
        config_path = project_path / ".agilegraph"
        if not config_path.exists():
            config_path = project_path / "agilegraph.json"

        domains_to_scan = []
        if config_path.exists():
            try:
                config_data = json.loads(config_path.read_text(encoding="utf-8"))
                domains_to_scan = config_data.get("ct_domains", [])
            except Exception as e:
                errors.append(
                    f"Failed to parse CT domains from config {config_path.name}: {str(e)}"
                )

        if not domains_to_scan:
            logger.info("No CT domains configured in .agilegraph file. Skipping CT scan.")
            return ScannerResult(
                scanner_name=self.name,
                status="success",
                findings=[],
                errors=errors,
                execution_time_ms=(time.time() - start_time) * 1000.0,
                metadata={"domains_scanned": 0},
            )

        # Instantiate dependencies for the service
        client = CTClient()
        parser = CTParser()
        service = CTService(client, parser)

        total_scanned = 0
        for domain in domains_to_scan:
            try:
                logger.info(f"Executing CT log query for {domain}...")
                ct_findings = service.scan_domain(domain, include_wildcards=True)
                total_scanned += 1

                # Map CTFindings to CryptoAssets for the ScannerResult
                for ctf in ct_findings:
                    asset = CryptoAsset(
                        asset_type=AssetType.CERTIFICATE,
                        algorithm=ctf.signature_algorithm or "Unknown",
                        language="Infrastructure",
                        file_path=config_path,  # Attaching to config file since it's external
                        line_number=None,
                        severity=ctf.severity,
                        confidence=1.0,
                        metadata={
                            "domain": domain,
                            "issuer": ctf.issuer_name,
                            "not_before": ctf.not_before,
                            "not_after": ctf.not_after,
                            "serial_number": ctf.serial_number,
                        },
                    )
                    findings.append(asset.model_dump(mode="json"))
            except Exception as e:
                errors.append(f"Failed to scan domain {domain}: {str(e)}")

        execution_time_ms = (time.time() - start_time) * 1000.0

        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={
                "domains_scanned": total_scanned,
                "total_ct_findings": len(findings),
            },
        )
