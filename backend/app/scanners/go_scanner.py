import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType

# Mapping known Go cryptographic packages to their AssetType and generic algorithm name
GO_API_MAPPING: Dict[str, Tuple[AssetType, str]] = {
    "crypto/aes": (AssetType.SYMMETRIC_KEY, "AES"),
    "crypto/des": (AssetType.SYMMETRIC_KEY, "DES"),
    "crypto/cipher": (AssetType.SYMMETRIC_KEY, "Cipher"),
    "crypto/md5": (AssetType.HASH, "MD5"),
    "crypto/sha1": (AssetType.HASH, "SHA-1"),
    "crypto/sha256": (AssetType.HASH, "SHA-256"),
    "crypto/rsa": (AssetType.ASYMMETRIC_KEY, "RSA"),
    "crypto/ecdsa": (AssetType.ASYMMETRIC_KEY, "ECDSA"),
    "crypto/ed25519": (AssetType.ASYMMETRIC_KEY, "Ed25519"),
    "crypto/hmac": (AssetType.HASH, "HMAC"),
    "crypto/tls": (AssetType.UNKNOWN, "TLS"),
    "crypto/x509": (AssetType.CERTIFICATE, "X.509"),
    "crypto/rand": (AssetType.UNKNOWN, "PRNG"),
    "golang.org/x/crypto": (AssetType.DEPENDENCY, "golang.org/x/crypto"),
}

class GoScanner(BaseScanner):
    """
    Scans Go source files (.go) to identify the use of standard library and 
    third-party cryptographic APIs via import statements.
    """
    
    @property
    def name(self) -> str:
        return "GoScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        return ["Go"]
        
    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        if project_path.exists() and project_path.is_dir():
            for file_path in sorted(project_path.rglob("*.go")):
                self._scan_file(file_path, findings, errors)
                
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={"files_scanned_patterns": ["*.go"]}
        )

    def _scan_file(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str]) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
            
            for line_idx, line in enumerate(content.splitlines()):
                line_str = line.strip()
                # Basic heuristic: look for imports matching the exact package strings
                if not line_str or line_str.startswith("//"):
                    continue
                
                for pkg_name, (asset_type, algorithm) in GO_API_MAPPING.items():
                    if f'"{pkg_name}"' in line_str or f"'{pkg_name}'" in line_str or pkg_name in line_str:
                        # Extract context to ensure it's imported or used
                        if "import" in line_str or '"' in line_str or "golang.org" in line_str:
                            asset = CryptoAsset(
                                asset_type=asset_type,
                                algorithm=algorithm,
                                language="Go",
                                file_path=file_path,
                                line_number=line_idx + 1,
                                severity=None,
                                confidence=0.8,
                                metadata={
                                    "package_name": pkg_name,
                                    "matched_line": line_str
                                }
                            )
                            findings.append(asset.model_dump(mode="json"))
                            
        except Exception as e:
            errors.append(f"Error reading {file_path}: {str(e)}")
