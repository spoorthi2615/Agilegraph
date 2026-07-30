import os
import sys
from pathlib import Path

def get_latest_mtime(paths):
    latest_time = 0
    latest_file = None
    
    for path_str in paths:
        path = Path(path_str)
        if path.is_file():
            mtime = path.stat().st_mtime
            if mtime > latest_time:
                latest_time = mtime
                latest_file = path
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for f in files:
                    # Ignore python cache files
                    if f.endswith('.pyc') or '__pycache__' in root:
                        continue
                    file_path = Path(root) / f
                    mtime = file_path.stat().st_mtime
                    if mtime > latest_time:
                        latest_time = mtime
                        latest_file = file_path
    return latest_time, latest_file

def main():
    print("Checking for document drift...")
    
    # Source code that impacts the pipeline
    code_paths = [
        "scripts/generate_gnn_dataset.py",
        "scripts/run_experiments.py",
        "scripts/statistical_tests.py",
        "scripts/generate_statistical_report.py",
        "scripts/generate_benchmark_report.py",
        "scripts/generate_ablation_report.py",
        "scripts/generate_readme_snippet.py",
        "scripts/report_helpers.py",
        "backend/app/ml/"
    ]
    
    # Data artifacts that impact the reports
    data_paths = [
        "research/results.json",
        "research/predictions.json",
        "research/statistical_results.json",
    ]
    
    # Generated research docs
    doc_paths = [
        "README.md",
        "research/statistical-analysis.md",
        "research/dataset-validation.md",
        "research/benchmark-study.md",
        "research/ablation-study.md"
    ]
    
    # Ensure all paths exist
    for p in code_paths + data_paths + doc_paths:
        if not os.path.exists(p):
            # Ignore missing data paths, they might not be generated yet
            if p in data_paths:
                continue
            print(f"Warning: Path '{p}' does not exist.")
            # If doc doesn't exist, we definitely have drift
            if p in doc_paths:
                print(f"ERROR: Required document '{p}' is missing. Please regenerate docs.")
                sys.exit(1)
    
    code_mtime, code_newest_file = get_latest_mtime(code_paths + data_paths)
    doc_mtime, doc_newest_file = get_latest_mtime(doc_paths)
    
    if code_mtime > doc_mtime:
        print(f"\n❌ DRIFT DETECTED!")
        print(f"File '{code_newest_file}' was modified more recently than your research docs.")
        print(f"This means your documentation might be reporting stale numbers.")
        
        # Check if the drift is due to data or code
        if any(str(code_newest_file).endswith(dp.split('/')[-1]) for dp in data_paths):
            print("The underlying results changed — re-run the report generators.")
        else:
            print("A generator script changed — re-run it, then verify output.")
            
        sys.exit(1)
        
    print(f"✅ Docs are up-to-date! (Code/Data: {code_newest_file}, Docs: {doc_newest_file})")
    
    # Run linter as secondary check
    try:
        from lint_generated_docs import lint_docs
        if not lint_docs():
            sys.exit(1)
    except ImportError:
        print("Warning: Could not import lint_generated_docs.py")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
