import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType

# Mapping known Java cryptographic API signatures to their AssetType and generic algorithm name
JAVA_API_MAPPING: Dict[str, Tuple[AssetType, str]] = {
    # Hashing
    'MessageDigest.getInstance("MD5")': (AssetType.HASH, "MD5"),
    'MessageDigest.getInstance("SHA-1")': (AssetType.HASH, "SHA-1"),
    'MessageDigest.getInstance("SHA-256")': (AssetType.HASH, "SHA-256"),
    
    # Symmetric Encryption
    'Cipher.getInstance("AES")': (AssetType.SYMMETRIC_KEY, "AES"),
    'Cipher.getInstance("DES")': (AssetType.SYMMETRIC_KEY, "DES"),
    'Cipher.getInstance("DESede")': (AssetType.SYMMETRIC_KEY, "3DES"),
    
    # Asymmetric Encryption
    'KeyPairGenerator.getInstance("RSA")': (AssetType.ASYMMETRIC_KEY, "RSA"),
    'KeyPairGenerator.getInstance("EC")': (AssetType.ASYMMETRIC_KEY, "ECC"),
    'KeyFactory.getInstance("RSA")': (AssetType.ASYMMETRIC_KEY, "RSA"),
    'KeyFactory.getInstance("EC")': (AssetType.ASYMMETRIC_KEY, "ECC"),
}

class JavaScanner(BaseScanner):
    """
    Statically analyzes Java source files to detect cryptographic API usage.
    """
    @property
    def name(self) -> str:
        return "JavaCryptoScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        return ["Java"]
        
    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        if project_path.exists() and project_path.is_dir():
            for file_path in project_path.rglob("*.java"):
                self._scan_java_file(file_path, findings, errors)
                
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={"files_scanned_pattern": "*.java"}
        )

    def _scan_java_file(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str]) -> None:
        """
        Parses a single Java file line-by-line to identify known cryptographic calls.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            for line_number, line in enumerate(content.splitlines(), start=1):
                # Basic normalization to skip pure comments and empty lines
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith("//"):
                    continue
                    
                # Scan for standard API usage
                for api_signature, (asset_type, algorithm) in JAVA_API_MAPPING.items():
                    if api_signature in stripped_line:
                        asset = CryptoAsset(
                            asset_type=asset_type,
                            algorithm=algorithm,
                            language="Java",
                            file_path=file_path,
                            line_number=line_number,
                            severity=None,
                            confidence=0.8,  # Heuristic confidence due to string matching limitations
                            metadata={
                                "matched_call": api_signature
                            }
                        )
                        findings.append(asset.model_dump(mode="json"))
                        
        except UnicodeDecodeError as e:
            errors.append(f"Encoding error parsing {file_path.name}: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error processing {file_path.name}: {str(e)}")
