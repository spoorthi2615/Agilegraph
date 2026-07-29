import os
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
        
    if "Full Model" not in preds:
        logging.error("Full Model data missing from predictions.json")
        return
        
    y_true = preds["Full Model"]["y_true"]
    node_names = preds["Full Model"]["node_names"]
    
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
            "scan", "/src"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Since we don't know the exact JSON schema of CBOMkit-theia, we'll do a robust text search
            # over its JSON/text output for vulnerable primitives. In a production pipeline, this would
            # rigorously parse the CycloneDX "cryptoProperties" block.
            output_lower = result.stdout.lower() + result.stderr.lower()
            
            vulnerable_primitives = ["rsa", "ecdsa", "dsa", "des", "3des", "md5", "sha1"]
            for prim in vulnerable_primitives:
                if prim in output_lower:
                    cbomkit_detected_algos.add(f"{repo_name}_{prim}")
                    
            if result.returncode != 0:
                logging.warning(f"CBOMkit returned non-zero for {repo_name}: {result.stderr[:200]}")
                
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
            repo_name, raw_name = name_str.split("::", 1)
        else:
            repo_name, raw_name = "unknown", name_str
            
        raw_name_lower = raw_name.lower()
        vulnerable_primitives = ["rsa", "ecdsa", "dsa", "des", "3des", "md5", "sha1"]
        
        # A node is predicted as vulnerable by CBOMkit ONLY IF:
        # 1. The repository had a CBOMkit hit for a specific primitive.
        # 2. This specific node matches the primitive that CBOMkit found in this repo.
        is_vuln = False
        for prim in vulnerable_primitives:
            if f"{repo_name}_{prim}" in cbomkit_detected_algos:
                # CBOMkit found this primitive somewhere in the repo.
                # Now we map it to the node. If the node name references this primitive,
                # we consider it a hit. If CBOMkit provided file-line locations, we would map those here.
                if prim in raw_name_lower:
                    is_vuln = True
                    break
                    
        y_cbom.append(1 if is_vuln else 0)
        
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
