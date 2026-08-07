from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.models.language import DetectedLanguage
from app.models.project_analysis import ProjectAnalysisResult
from app.scanners.scanner_manager import ScannerManager
from app.scanners.scanner_registry import ScannerRegistry
from app.services.language_detection_service import LanguageDetectionService


class ProjectAnalysisService:
    """
    Orchestrates the entire static analysis pipeline for a project,
    coordinating language detection and scanner execution efficiently.
    """

    def __init__(self, registry: ScannerRegistry):
        self.registry = registry
        # We compose the manager internally using the provided registry
        self.scanner_manager = ScannerManager(self.registry)

    def analyze_project(self, project_id: str, project_path: Path) -> ProjectAnalysisResult:
        """
        Executes the full orchestration pipeline on a given project path.
        """
        # Step 1: Detect programming languages via the dedicated service
        detected_languages: List[DetectedLanguage] = LanguageDetectionService.detect_languages(
            project_path
        )

        # Step 2: Determine target languages for dynamic scanner filtering
        target_languages = [dl.language for dl in detected_languages]

        # Step 3: Delegate scanner execution to the ScannerManager
        # It handles routing to specific scanners based on the target languages
        scanner_results = self.scanner_manager.execute_all(
            project_path, target_languages=target_languages
        )

        # Step 4: Collect comprehensive metrics from all ScannerResult objects
        total_findings = sum(len(result.findings) for result in scanner_results)
        total_errors = sum(len(result.errors) for result in scanner_results)
        executed_scanners = [result.scanner_name for result in scanner_results]

        # Step 5: Construct and return the final orchestration result
        return ProjectAnalysisResult(
            project_id=project_id,
            detected_languages=detected_languages,
            executed_scanners=executed_scanners,
            scanner_results=scanner_results,
            total_findings=total_findings,
            total_errors=total_errors,
            analysis_completed_at=datetime.now(timezone.utc),
        )
