from pathlib import Path
from typing import List
from app.scanners.scanner_registry import ScannerRegistry
from app.scanners.scanner_result import ScannerResult

class ScannerManager:
    """
    Manages the execution flow of multiple scanners against a target project.
    """
    def __init__(self, registry: ScannerRegistry) -> None:
        self.registry = registry
        
    def execute_all(self, project_path: Path) -> List[ScannerResult]:
        """
        Sequentially executes all registered scanners against the project path.
        """
        results: List[ScannerResult] = []
        scanner_names = self.registry.list_scanners()
        
        for name in scanner_names:
            scanner_class = self.registry.get(name)
            
            try:
                # Instantiate a fresh scanner before executing scan()
                scanner = scanner_class()
                
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
