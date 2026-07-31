from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging

from app.scanners.scanner_registry import ScannerRegistry
from app.scanners.scanner_result import ScannerResult

logger = logging.getLogger(__name__)

# Hard per-scanner wall-clock timeout (seconds). Prevents any scanner from hanging the pipeline.
SCANNER_TIMEOUT_SECONDS = 90

class ScannerManager:
    """
    Manages the execution flow of multiple scanners against a target project.
    Each scanner is run in a thread with a hard timeout so no single scanner
    can block the entire pipeline.
    """
    def __init__(self, registry: ScannerRegistry) -> None:
        self.registry = registry
        
    def execute_all(self, project_path: Path, target_languages: Optional[List[str]] = None) -> List[ScannerResult]:
        """
        Sequentially executes all registered scanners against the project path.
        If target_languages is provided, only scanners supporting those languages are executed.
        Each scanner runs inside a thread with a hard wall-clock timeout.
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
                    # "All" is a wildcard — always runs regardless of detected languages
                    supported = set(scanner.supported_languages)
                    targets = set(target_languages)
                    if "All" not in supported and not supported.intersection(targets):
                        logger.debug(f"Skipping scanner '{name}' (language mismatch)")
                        continue
                
                logger.info(f"Running scanner '{name}' with {SCANNER_TIMEOUT_SECONDS}s timeout...")
                
                # Run the scanner in a thread with a hard timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(scanner.scan, project_path)
                    try:
                        result = future.result(timeout=SCANNER_TIMEOUT_SECONDS)
                        results.append(result)
                        logger.info(f"Scanner '{name}' completed: {len(result.findings)} findings")
                    except FutureTimeoutError:
                        logger.warning(f"Scanner '{name}' timed out after {SCANNER_TIMEOUT_SECONDS}s — skipping.")
                        future.cancel()
                        results.append(
                            ScannerResult(
                                scanner_name=name,
                                status="timeout",
                                findings=[],
                                errors=[f"Scanner timed out after {SCANNER_TIMEOUT_SECONDS} seconds."],
                                execution_time_ms=SCANNER_TIMEOUT_SECONDS * 1000.0,
                                metadata={}
                            )
                        )
            except Exception as e:
                # If a scanner raises an unhandled exception, gracefully catch it
                # and return an error payload so other scanners can continue.
                logger.error(f"Scanner '{name}' raised an exception: {e}")
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
