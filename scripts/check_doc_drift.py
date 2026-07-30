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

import json

def check_pipeline_stage_freshness():
    res_path = Path("research/results.json")
    stats_path = Path("research/statistical_results.json")
    
    if not res_path.exists() or not stats_path.exists():
        return # Skip if they don't exist yet
        
    try:
        with open(res_path, "r") as f:
            res_data = json.load(f)
        with open(stats_path, "r") as f:
            stats_data = json.load(f)
            
        res_run_id = res_data.get("run_id")
        stat_run_id = stats_data.get("run_id")
        
        if res_run_id and stat_run_id and res_run_id != stat_run_id:
            print("❌ PIPELINE DRIFT: research/results.json (run_id) does not match research/statistical_results.json.")
            print("   Run `python scripts/statistical_tests.py` before regenerating reports.")
            sys.exit(1)
            
        if not res_run_id or not stat_run_id:
            # Fallback to mtime
            if res_path.stat().st_mtime > stats_path.stat().st_mtime:
                print("❌ PIPELINE DRIFT: research/results.json is newer than research/statistical_results.json.")
                print("   Run `python scripts/statistical_tests.py` before regenerating reports.")
                sys.exit(1)
    except Exception as e:
        print(f"Warning: Error checking pipeline freshness: {e}")

def main():
    print("Checking for document drift...")
    check_pipeline_stage_freshness()
    
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
        "research/ablation-study.md",
        "research/status-and-limitations.md",
        "research/threats-to-validity.md"
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
        print("\n❌ DRIFT DETECTED!")
        print(f"File '{code_newest_file}' was modified more recently than your research docs.")
        print("This means your documentation might be reporting stale numbers.")
        
        # Check if the drift is due to data or code
        if any(str(code_newest_file).endswith(dp.split('/')[-1]) for dp in data_paths):
            print("The underlying results changed — re-run the report generators.")
        else:
            print("A generator script changed — re-run it, then verify output.")
            
        sys.exit(1)
        
    print(f"✅ Docs are up-to-date! (Code/Data: {code_newest_file}, Docs: {doc_newest_file})")
    
    # Run linter as secondary check
    try:
        from lint_generated_docs import lint_docs, check_cross_doc_consistency
        doc_paths_for_lint = [
            "README.md",
            "research/statistical-analysis.md",
            "research/dataset-validation.md",
            "research/benchmark-study.md",
            "research/ablation-study.md",
            "research/status-and-limitations.md",
        ]
        lint_ok = lint_docs()
        consistency_ok = check_cross_doc_consistency(doc_paths_for_lint)
        if not (lint_ok and consistency_ok):
            sys.exit(1)
    except ImportError:
        print("Warning: Could not import lint_generated_docs.py")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
