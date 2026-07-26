from pathlib import Path
from typing import List, Optional
from app.scanners.scanner_registry import ScannerRegistry
from app.scanners.scanner_result import ScannerResult

class ScannerManager:
    """
    Manages the execution flow of multiple scanners against a target project.
    """
    def __init__(self, registry: ScannerRegistry) -> None:
        self.registry = registry
        
    def execute_all(self, project_path: Path, target_languages: Optional[List[str]] = None) -> List[ScannerResult]:
        """
        Sequentially executes all registered scanners against the project path.
        If target_languages is provided, only scanners supporting those languages are executed.
        """
        results: List[ScannerResult] = []
        scanner_names = self.registry.list_scanners()
        
        for name in scanner_names:
            scanner_class = self.registry.get(name)
            
            try:
                # Instantiate a fresh scanner before executing scan()
                scanner = scanner_class()
                
                if target_languages is not None:
                    # Verify intersection between detected languages and the scanner's supported languages
                    supported = set(scanner.supported_languages)
                    targets = set(target_languages)
                    if not supported.intersection(targets):
                        continue
                
                
                # Execute the scanner and collect the standard result
                result = scanner.scan(project_path)
                results.append(result)
            except Exception as e:
                # If a scanner raises an unhandled exception, gracefully catch it
                # and return an error payload so other scanners can continue.
                results.append(
                    ScannerResult(
                        scanner_name=name,
                        status="error",
                        findings=[],
                        errors=[str(e)],
                        execution_time_ms=0.0,
                        metadata={}
                    )
                )
                
        return results
