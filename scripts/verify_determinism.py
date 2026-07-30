import subprocess
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    logging.info("Running generate_gnn_dataset.py...")
    subprocess.run(["python", "scripts/generate_gnn_dataset.py"], check=True)
    
    logging.info("Running run_experiments.py...")
    subprocess.run(["python", "scripts/run_experiments.py"], check=True)
    
    results_path = Path("research/results.json")
    if not results_path.exists():
        raise FileNotFoundError("research/results.json was not generated.")
        
    with open(results_path, "r") as f:
        return json.load(f)

def main():
    logging.info("=== Starting Determinism Smoke Test ===")
    
    # Run 1
    logging.info("--- Run 1 ---")
    results1 = run_pipeline()
    
    # Run 2
    logging.info("--- Run 2 ---")
    results2 = run_pipeline()
    
    # Compare F1 scores
    f1_dict1 = results1.get("ablation_f1", {})
    f1_dict2 = results2.get("ablation_f1", {})
    
    all_match = True
    tolerance = 1e-3  # Allow very small floating point diffs if unavoidable
    
    for model in f1_dict1:
        if model not in f1_dict2:
            logging.error(f"Model {model} missing in Run 2!")
            all_match = False
            continue
            
        m1 = f1_dict1[model]["mean"]
        m2 = f1_dict2[model]["mean"]
        
        diff = abs(m1 - m2)
        if diff > tolerance:
            logging.error(f"Determinism failed for {model}: Run1={m1}, Run2={m2}, Diff={diff}")
            all_match = False
        else:
            logging.info(f"Determinism passed for {model}: Run1={m1}, Run2={m2}")
            
    if all_match:
        logging.info("✅ SUCCESS: Pipeline is completely deterministic!")
    else:
        logging.error("❌ FAILED: Pipeline exhibits run-to-run nondeterminism.")
        exit(1)

if __name__ == "__main__":
    main()
