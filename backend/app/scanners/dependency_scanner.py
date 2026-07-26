import time
import tomllib
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.scanners.base_scanner import BaseScanner
from app.scanners.scanner_result import ScannerResult
from app.models.crypto_asset import CryptoAsset, AssetType

class DependencyScanner(BaseScanner):
    """
    Scans Python project manifest files to discover software dependencies.
    """
    @property
    def name(self) -> str:
        return "PythonDependencyScanner"
        
    @property
    def supported_languages(self) -> List[str]:
        return ["Python", "Go"]
        
    def scan(self, project_path: Path) -> ScannerResult:
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        if project_path.exists() and project_path.is_dir():
            processed_deps: set = set()
            # Traverse the project only once
            for file_path in project_path.rglob("*"):
                if file_path.name == "requirements.txt":
                    self._parse_requirements_txt(file_path, findings, errors, processed_deps)
                elif file_path.name == "pyproject.toml":
                    self._parse_pyproject_toml(file_path, findings, errors, processed_deps)
                elif file_path.name in ("go.mod", "go.sum"):
                    self._parse_go_mod(file_path, findings, errors, processed_deps)
                    
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        return ScannerResult(
            scanner_name=self.name,
            status="success" if not errors else "completed_with_errors",
            findings=findings,
            errors=errors,
            execution_time_ms=execution_time_ms,
            metadata={"files_scanned_patterns": ["requirements.txt", "pyproject.toml", "go.mod", "go.sum"]}
        )
        
    def _create_dependency_asset(self, package_name: str, version: Optional[str], file_path: Path) -> Dict[str, Any]:
        """
        Creates a CryptoAsset from discovered dependency data.
        """
        asset = CryptoAsset(
            asset_type=AssetType.DEPENDENCY,
            algorithm=package_name,
            language="Unknown" if file_path.suffix not in [".mod", ".sum"] else "Go", # We can refine this later
            file_path=file_path,
            line_number=None,
            severity=None,
            confidence=1.0,
            metadata={
                "package_name": package_name,
                "version": version if version else "unknown",
                "manifest_file": file_path.name
            }
        )
        return asset.model_dump(mode="json")
        
    def _parse_requirements_txt(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str], processed_deps: set) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                # Ignore comments, blank lines, and unsupported directives
                if not line or line.startswith(("#", "-e", "git+", "http", "/", "\\", "-r", "--")):
                    continue
                if ";" in line:
                    continue
                
                package_name, version = self._extract_package_and_version(line)
                if package_name:
                    dep_key = (package_name.lower(), version)
                    if dep_key in processed_deps:
                        continue
                    processed_deps.add(dep_key)
                    findings.append(self._create_dependency_asset(package_name, version, file_path))
                    
        except Exception as e:
            errors.append(f"Error parsing requirements.txt at {file_path}: {str(e)}")

    def _parse_pyproject_toml(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str], processed_deps: set) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
            data = tomllib.loads(content)
            
            project_data = data.get("project", {})
            dependencies = project_data.get("dependencies", [])
            
            for dep in dependencies:
                line = dep.strip()
                if ";" in line:
                    continue
                    
                package_name, version = self._extract_package_and_version(line)
                if package_name:
                    dep_key = (package_name.lower(), version)
                    if dep_key in processed_deps:
                        continue
                    processed_deps.add(dep_key)
                    findings.append(self._create_dependency_asset(package_name, version, file_path))
                    
        except Exception as e:
            errors.append(f"Error parsing pyproject.toml at {file_path}: {str(e)}")

    def _extract_package_and_version(self, line: str) -> tuple[str, Optional[str]]:
        """
        Extracts package name and version specifier from a dependency string.
        """
        delimiters = ["==", ">=", "<=", "~=", ">", "<", "!="]
        package_name = line
        version = None
        
        for delim in delimiters:
            if delim in package_name:
                parts = package_name.split(delim, 1)
                package_name = parts[0].strip()
                version = f"{delim}{parts[1].strip()}"
                break
                
            package_name = package_name.split("[")[0].strip()
            
        return package_name, version

    def _parse_go_mod(self, file_path: Path, findings: List[Dict[str, Any]], errors: List[str], processed_deps: set) -> None:
        try:
            content = file_path.read_text(encoding="utf-8")
            in_require_block = False
            
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                    
                if line == "require (":
                    in_require_block = True
                    continue
                elif line == ")" and in_require_block:
                    in_require_block = False
                    continue
                    
                # Direct requires in go.mod look like: "require github.com/foo/bar v1.2.3"
                if line.startswith("require "):
                    parts = line.split()
                    if len(parts) >= 3:
                        package_name = parts[1]
                        version = parts[2]
                        self._add_go_dep(package_name, version, file_path, findings, processed_deps)
                elif in_require_block or file_path.name == "go.sum":
                    # Lines inside require() block or in go.sum
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[0]
                        version = parts[1]
                        self._add_go_dep(package_name, version, file_path, findings, processed_deps)
                        
        except Exception as e:
            errors.append(f"Error parsing {file_path.name} at {file_path}: {str(e)}")
            
    def _add_go_dep(self, package_name: str, version: str, file_path: Path, findings: List[Dict[str, Any]], processed_deps: set) -> None:
        dep_key = (package_name.lower(), version)
        if dep_key in processed_deps:
            return
        processed_deps.add(dep_key)
        
        # We temporarily override the asset creation logic for Go dependencies
        asset = CryptoAsset(
            asset_type=AssetType.DEPENDENCY,
            algorithm=package_name,
            language="Go",
            file_path=file_path,
            line_number=None,
            severity=None,
            confidence=1.0,
            metadata={
                "package_name": package_name,
                "version": version,
                "manifest_file": file_path.name
            }
        )
        findings.append(asset.model_dump(mode="json"))
