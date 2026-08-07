import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.scanners.scanner_registry import get_default_registry
from app.services.project_analysis_service import ProjectAnalysisService


def test_integration_pipeline():
    """
    Genuine End-to-End integration test.
    Executes the real ProjectAnalysisService against the WebGoat repository,
    invoking all registered static scanners, and validates that findings are produced.
    """
    print("=== AgileGraph Genuine Integration Test ===")

    # 1. Initialize real registry
    registry = get_default_registry()
    print(f"Loaded Scanners: {registry.list_scanners()}")

    service = ProjectAnalysisService(registry)

    # 2. Target a real repository
    # REGRESSION PREVENTION: Do not hardcode "backend/data/...".
    # Pytest is often run from the `backend/` directory, causing relative paths
    # like "backend/..." to fail. Resolve dynamically via __file__ to guarantee safety.
    target_repo = Path(__file__).parent.parent / "data" / "corpus" / "WebGoat"
    if not target_repo.exists() or not list(target_repo.iterdir()):
        print(f"ERROR: WebGoat repository not found at {target_repo}.")
        print("Please run fetch_github_corpus.py first.")
        sys.exit(1)

    print(f"Scanning target: {target_repo}")

    # 3. Execute genuine analysis pipeline
    try:
        result = service.analyze_project("integration-test-webgoat", target_repo)

        # 4. Assert physical findings
        total_findings = sum(len(scanner.findings) for scanner in result.scanner_results)

        print("\n--- Test Results ---")
        print(f"Total Findings Discovered: {total_findings}")
        for scanner in result.scanner_results:
            print(f"- {scanner.scanner_name}: {len(scanner.findings)} findings")

        if total_findings > 0:
            print("\nSTATUS: PASS. Real vulnerabilities successfully detected across the pipeline.")
            return
        else:
            print("\nSTATUS: FAIL. Pipeline executed but zero findings were returned.")
            raise AssertionError("Pipeline executed but zero findings were returned.")

    except Exception as e:
        print(f"\nSTATUS: FAIL. Unhandled exception during pipeline execution: {str(e)}")
        raise e


if __name__ == "__main__":
    test_integration_pipeline()
