import time
import warnings
import logging
from pathlib import Path
from typing import List, Dict, Any

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, ed448

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType

class CertificateScanner(BaseScanner):
    """
    Scans the project for X.509 certificate files and extracts their metadata.
    """
    @property
    def name(self) -> str:
        return "CertificateScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        # Certificates are language-agnostic. To ensure the orchestration layer executes this
        # scanner across any detected project, we return a broad list of potential languages.
        return [
            "Python", "Java", "Go", "JavaScript", "TypeScript", 
            "C", "C++", "C#", "Ruby", "PHP", "Rust", "Kotlin", "Swift"
        ]

    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        target_extensions = {".pem", ".crt", ".cer", ".der"}
        
        if project_path.exists() and project_path.is_dir():
            for file_path in project_path.rglob("*"):
                if file_path.suffix.lower() in target_extensions:
                    self._parse_certificate(file_path, findings, errors)
                    
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={"extensions_scanned": list(target_extensions)}
        )

    def _parse_certificate(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str]) -> None:
        try:
            content = file_path.read_bytes()
            
            # Attempt PEM parsing, fallback to DER parsing
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                try:
                    cert = x509.load_pem_x509_certificate(content)
                except Exception:
                    try:
                        cert = x509.load_der_x509_certificate(content)
                    except Exception as inner_e:
                        raise ValueError(f"Could not parse as PEM or DER: {inner_e}")
                        
                for w in caught_warnings:
                    logging.warning(f"Certificate Scanner Warning in {file_path.name}: {w.message}")
                    
            # Extract basic identifiers
            subject = self._get_name_string(cert.subject)
            issuer = self._get_name_string(cert.issuer)
            serial_number = str(cert.serial_number)
            
            # Extract signature algorithm
            signature_algorithm = cert.signature_algorithm_oid._name
            if not signature_algorithm:
                signature_algorithm = "Unknown"
                
            # Extract public key algorithm
            public_key = cert.public_key()
            public_key_algo = self._get_public_key_algorithm(public_key)
            
            # Handle cryptography library deprecations gracefully for datetimes
            if hasattr(cert, "not_valid_before_utc"):
                valid_from = cert.not_valid_before_utc.isoformat()
                valid_until = cert.not_valid_after_utc.isoformat()
            else:
                valid_from = cert.not_valid_before.isoformat()
                valid_until = cert.not_valid_after.isoformat()
            
            asset = CryptoAsset(
                asset_type=AssetType.CERTIFICATE,
                algorithm=public_key_algo,
                language=None,
                file_path=file_path,
                line_number=None,
                severity=None,
                confidence=1.0,
                metadata={
                    "subject": subject,
                    "issuer": issuer,
                    "serial_number": serial_number,
                    "signature_algorithm": signature_algorithm,
                    "valid_from": valid_from,
                    "valid_until": valid_until
                }
            )
            
            findings.append(asset.model_dump(mode="json"))
            
        except Exception as e:
            errors.append(f"Error parsing certificate at {file_path}: {str(e)}")
            
    def _get_name_string(self, name: x509.Name) -> str:
        """
        Extracts a readable string from an X.509 Name attribute (e.g. Common Name).
        Falls back to RFC 4514 string representation if CN is missing.
        """
        attributes = name.get_attributes_for_oid(NameOID.COMMON_NAME)
        if attributes:
            return str(attributes[0].value)
        return name.rfc4514_string()

    def _get_public_key_algorithm(self, public_key: Any) -> str:
        """
        Identifies the core algorithm used in the public key.
        """
        if isinstance(public_key, rsa.RSAPublicKey):
            return "RSA"
        elif isinstance(public_key, dsa.DSAPublicKey):
            return "DSA"
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            return f"ECC ({public_key.curve.name})"
        elif isinstance(public_key, ed25519.Ed25519PublicKey):
            return "Ed25519"
        elif isinstance(public_key, ed448.Ed448PublicKey):
            return "Ed448"
        return "Unknown"
