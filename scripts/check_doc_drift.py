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
        "backend/app/ml/"
    ]
    
    # Generated research docs
    doc_paths = [
        "research/statistical-analysis.md",
        "research/dataset-validation.md",
        "research/benchmark-study.md",
        "research/ablation-study.md"
    ]
    
    # Ensure all paths exist
    for p in code_paths + doc_paths:
        if not os.path.exists(p):
            print(f"Warning: Path '{p}' does not exist.")
            # If doc doesn't exist, we definitely have drift
            if p in doc_paths:
                print(f"ERROR: Required document '{p}' is missing. Please regenerate docs.")
                sys.exit(1)
    
    code_mtime, code_newest_file = get_latest_mtime(code_paths)
    doc_mtime, doc_newest_file = get_latest_mtime(doc_paths)
    
    if code_mtime > doc_mtime:
        print(f"\n❌ DRIFT DETECTED!")
        print(f"Code file '{code_newest_file}' was modified more recently than your research docs.")
        print(f"This means your documentation might be reporting stale numbers.")
        print(f"Please re-run the pipeline and/or `python scripts/generate_statistical_report.py` to update the docs.")
        sys.exit(1)
        
    print(f"✅ Docs are up-to-date! (Code: {code_newest_file}, Docs: {doc_newest_file})")
    sys.exit(0)

if __name__ == "__main__":
    main()
