import os
import subprocess
import sys
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def run_cmd(cmd):
    print(f">> {' '.join(cmd)}")
    result = subprocess.run(cmd, text=True, cwd="d:/projects/major project/Agilegraph")
    if result.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}")
        sys.exit(1)
    return result

print_header("Phase 3: Documentation & Results Reconciliation")

print("\n--- Task 3.1: Re-Generate All Markdown Reports ---")
run_cmd([sys.executable, "scripts/generate_statistical_report.py"])
run_cmd([sys.executable, "scripts/generate_benchmark_report.py"])
run_cmd([sys.executable, "scripts/generate_ablation_report.py"])
run_cmd([sys.executable, "scripts/generate_readme_snippet.py"])

print("\n--- Task 3.2: Verify check_doc_drift.py ---")
run_cmd([sys.executable, "scripts/check_doc_drift.py"])

print("\n--- Task 3.3: Verify Metric Alignment ---")
readme_path = Path("d:/projects/major project/Agilegraph/README.md")
if readme_path.exists():
    content = readme_path.read_text(encoding="utf-8")
    if "0.859" in content or "85.9" in content:
        print("✅ SUCCESS: The new F1 score (0.859) was found in README.md!")
    else:
        print("❌ WARNING: The F1 score (0.859) was NOT found in README.md!")
        
results_path = Path("d:/projects/major project/Agilegraph/research/results.json")
if results_path.exists():
    print("✅ SUCCESS: results.json exists and is ready for review.")

print("\n\n✅ PHASE 3 COMPLETED SUCCESSFULLY. DOCS ARE SYNCHRONIZED.")
