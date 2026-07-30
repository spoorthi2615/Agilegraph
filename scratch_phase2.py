import os
import subprocess
import shutil
import sys
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

print_header("Phase 2: Establish a Single Source of Truth for Metrics")

print("\n--- Task 2.1: Verify Corpus Fetch Logic ---")
run_cmd([sys.executable, "scripts/fetch_github_corpus.py"])

print("\n--- Task 2.2: Regenerate GNN Dataset ---")
tensors_dir = Path("d:/projects/major project/Agilegraph/backend/data/tensors")
if tensors_dir.exists():
    shutil.rmtree(tensors_dir)
tensors_dir.mkdir(parents=True, exist_ok=True)
run_cmd([sys.executable, "scripts/generate_gnn_dataset.py"])

print("\n--- Task 2.4 / 2.3: Purge Stale Results & Run Training ---")
for f in ["research/results.json", "research/statistical_results.json", "research/predictions.json"]:
    path = Path("d:/projects/major project/Agilegraph") / f
    if path.exists():
        path.unlink()
        print(f"Deleted stale file: {f}")

run_cmd([sys.executable, "scripts/run_experiments.py"])
run_cmd([sys.executable, "scripts/statistical_tests.py"])

print("\n--- Task 2.5: Run CBOMkit Baseline ---")
run_cmd([sys.executable, "scripts/run_cbomkit.py"])

print("\n\n✅ PHASE 2 COMPLETED SUCCESSFULLY. PIPELINE IS SYNCHRONIZED.")
