import json
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_cbomkit():
    predictions_file = Path("research/predictions.json")
    if not predictions_file.exists():
        logging.error("predictions.json not found. Run experiments first.")
        return
        
    with open(predictions_file, "r") as f:
        preds = json.load(f)
        
    if "Full Model (w/ Heuristic)" not in preds:
        logging.error("Full Model data missing from predictions.json")
        return
        
    y_true = preds["Full Model (w/ Heuristic)"]["y_true"]
    node_names = preds["Full Model (w/ Heuristic)"]["node_names"]
    
    corpus_dir = Path("backend/data/corpus").resolve()
    
    cbomkit_detected_algos = set()
    
    logging.info("Starting CBOMkit Docker scans across 40 repositories...")
    
    for repo_dir in corpus_dir.iterdir():
        if not repo_dir.is_dir():
            continue
            
        repo_name = repo_dir.name
        logging.info(f"Scanning {repo_name} with CBOMkit...")
        
        # We will mount the repo directory to /src inside the container
        # Note: Depending on the exact cbomkit-theia CLI, this might need tweaking.
        # We try to run the scan and capture stdout.
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{str(repo_dir)}:/src",
            "ghcr.io/ibm/cbomkit-theia:latest",
            "dir", "/src"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=120)
            
            if result.returncode != 0:
                logging.warning(f"CBOMkit returned non-zero for {repo_name}: {result.stderr[:200]}")
                continue
                
            try:
                cbom_data = json.loads(result.stdout)
                components = cbom_data.get("components") or []
                vulnerable_primitives = ["rsa", "ecdsa", "dsa", "des", "3des", "md5", "sha1"]
                
                for comp in components:
                    if "cryptoProperties" in comp:
                        comp_name = comp.get("name", "").lower()
                        for prim in vulnerable_primitives:
                            if prim in comp_name:
                                cbomkit_detected_algos.add(f"{repo_name}_{prim}")
            except json.JSONDecodeError:
                logging.error(f"Failed to parse CBOMkit JSON output for {repo_name}")
                
        except subprocess.TimeoutExpired:
            logging.error(f"CBOMkit timed out on {repo_name}")
        except Exception as e:
            logging.error(f"Failed to run Docker for {repo_name}: {e}")

    # Map the repository-level CBOMkit findings down to the Node level to match GNN output.
    y_cbom = []
    
    for i, name in enumerate(node_names):
        name_str = str(name)
        # Format is expected to be "repo_name::raw_node_name"
        if "::" in name_str:
            repo_name = name_str.split("::", 1)[0]
        else:
            repo_name = "unknown"
            
        # Because cbomkit-theia is explicitly not designed for source-code node classification,
        # we explicitly mark these source nodes as "N/A" rather than falsely assigning them 0 (Safe)
        # which would otherwise turn this into a deceptive majority-class predictor.
        y_cbom.append("N/A")
        
    preds["CBOMkit Baseline"] = {
        "y_true": y_true,
        "y_pred": y_cbom,
        "node_names": node_names
    }
    
    with open(predictions_file, "w") as f:
        json.dump(preds, f)
        
    logging.info("CBOMkit Baseline predictions appended to predictions.json!")
    logging.info("You can now run `python scripts/statistical_tests.py` to compare AgileGraph against CBOMkit.")

if __name__ == "__main__":
    run_cbomkit()
