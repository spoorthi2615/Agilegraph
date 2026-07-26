import ast
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType, Severity

# Pre-defined mapping of known API calls to their respective AssetType and Algorithm
API_MAPPING: Dict[str, Tuple[AssetType, str]] = {
    # Hashlib
    "hashlib.md5": (AssetType.HASH, "MD5"),
    "md5": (AssetType.HASH, "MD5"),
    "hashlib.sha1": (AssetType.HASH, "SHA-1"),
    "sha1": (AssetType.HASH, "SHA-1"),
    "hashlib.sha224": (AssetType.HASH, "SHA-224"),
    "sha224": (AssetType.HASH, "SHA-224"),
    "hashlib.sha256": (AssetType.HASH, "SHA-256"),
    "sha256": (AssetType.HASH, "SHA-256"),
    "hashlib.sha384": (AssetType.HASH, "SHA-384"),
    "sha384": (AssetType.HASH, "SHA-384"),
    "hashlib.sha512": (AssetType.HASH, "SHA-512"),
    "sha512": (AssetType.HASH, "SHA-512"),
    
    # HMAC
    "hmac.new": (AssetType.HASH, "HMAC"),
    
    # Secrets
    "secrets.token_bytes": (AssetType.KEY, "Random"),
    "secrets.token_hex": (AssetType.KEY, "Random"),
    "secrets.token_urlsafe": (AssetType.KEY, "Random"),
    
    # SSL
    "ssl.create_default_context": (AssetType.CERTIFICATE, "SSL/TLS"),
    "ssl.SSLContext": (AssetType.CERTIFICATE, "SSL/TLS"),
    
    # JWT
    "jwt.encode": (AssetType.JWT, "JWT"),
    "jwt.decode": (AssetType.JWT, "JWT"),
    
    # PyCryptodome Symmetric
    "AES.new": (AssetType.SYMMETRIC_KEY, "AES"),
    "DES.new": (AssetType.SYMMETRIC_KEY, "DES"),
    "DES3.new": (AssetType.SYMMETRIC_KEY, "3DES"),
    
    # PyCryptodome Asymmetric
    "RSA.generate": (AssetType.ASYMMETRIC_KEY, "RSA"),
    "RSA.import_key": (AssetType.ASYMMETRIC_KEY, "RSA"),
    "ECC.generate": (AssetType.ASYMMETRIC_KEY, "ECC"),
    "ECC.import_key": (AssetType.ASYMMETRIC_KEY, "ECC"),
}

class CryptoAstVisitor(ast.NodeVisitor):
    """
    AST Visitor that parses a Python abstract syntax tree to identify 
    known cryptographic API calls without relying on alias resolution.
    """
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.findings: List[CryptoAsset] = []

    def _get_call_name(self, node: ast.expr) -> str:
        """
        Recursively extracts the dotted name of an AST expression (e.g., 'hashlib.md5').
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base_name = self._get_call_name(node.value)
            if base_name:
                return f"{base_name}.{node.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """
        Intercepts function calls in the AST to check against the known API list.
        """
        call_name = self._get_call_name(node.func)
        
        if call_name in API_MAPPING:
            asset_type, algorithm = API_MAPPING[call_name]
            
            asset = CryptoAsset(
                asset_type=asset_type,
                algorithm=algorithm,
                language="Python",
                file_path=self.file_path,
                line_number=node.lineno,
                confidence=0.8,  # Heuristic confidence since we lack alias resolution
                metadata={"matched_call": call_name}
            )
            self.findings.append(asset)
            
        # Continue traversing the AST
        self.generic_visit(node)


class PythonScanner(BaseScanner):
    """
    Scans a Python project using standard library 'ast' to detect 
    cryptographic API usage statically.
    """
    
    @property
    def name(self) -> str:
        return "PythonCryptoScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        return ["Python"]
        
    def scan(self, project_path: Path) -> ScannerResult:
        """
        Executes the AST-based scan on all Python files within the project.
        """
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        if project_path.exists() and project_path.is_dir():
            for file_path in project_path.rglob("*.py"):
                try:
                    source_code = file_path.read_text(encoding="utf-8")
                    tree = ast.parse(source_code, filename=str(file_path))
                    
                    visitor = CryptoAstVisitor(file_path)
                    visitor.visit(tree)
                    
                    # Convert findings to dictionary representations for ScannerResult
                    for finding in visitor.findings:
                        findings.append(finding.model_dump(mode="json"))
                        
                except SyntaxError as e:
                    # Continue scanning after syntax errors as requested
                    errors.append(f"Syntax error in {file_path.name}: {str(e)}")
                    continue
                except UnicodeDecodeError as e:
                    errors.append(f"Encoding error in {file_path.name}: {str(e)}")
                    continue
                except Exception as e:
                    errors.append(f"Unexpected error analyzing {file_path.name}: {str(e)}")
                    continue
                    
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={"files_scanned_pattern": "*.py"}
        )
