import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.project_analysis_service import ProjectAnalysisService
from app.scanners.scanner_registry import get_default_registry

def run_integration_test():
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
    target_repo = Path("data/corpus/WebGoat")
    if not target_repo.exists() or not list(target_repo.iterdir()):
        print("ERROR: WebGoat repository not found in data/corpus/WebGoat.")
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
            sys.exit(0)
        else:
            print("\nSTATUS: FAIL. Pipeline executed but zero findings were returned.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nSTATUS: FAIL. Unhandled exception during pipeline execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_integration_test()
