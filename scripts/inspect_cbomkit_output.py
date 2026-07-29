import os
import subprocess
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')

def inspect_cbomkit():
    corpus_dir = Path("backend/data/corpus").resolve()
    
    if not corpus_dir.exists():
        logging.error("Corpus directory not found.")
        return
        
    repos = [p for p in corpus_dir.iterdir() if p.is_dir()][:5]
    if not repos:
        logging.error("No repositories found in corpus.")
        return
        
    logging.info(f"Dry-running CBOMkit against {len(repos)} repos...")
    
    for repo_dir in repos:
        repo_name = repo_dir.name
        logging.info(f"\n--- Repository: {repo_name} ---")
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{str(repo_dir)}:/src",
            "ghcr.io/ibm/cbomkit-theia:latest",
            "dir", "/src"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=120)
            logging.info(f"Return Code: {result.returncode}")
            
            if result.returncode != 0:
                logging.error(f"Error Output:\n{result.stderr[:500]}")
                continue
                
            try:
                cbom_data = json.loads(result.stdout)
                components = cbom_data.get("components", [])
                logging.info(f"Total Components found: {len(components)}")
                
                crypto_comps = [c for c in components if "cryptoProperties" in c]
                logging.info(f"Crypto-relevant Components: {len(crypto_comps)}")
                
                if crypto_comps:
                    logging.info(f"Sample crypto component: {crypto_comps[0].get('name')}")
                    
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON. Raw Output:\n{result.stdout[:500]}")
                
        except subprocess.TimeoutExpired:
            logging.error("Timed out.")
        except Exception as e:
            logging.error(f"Failed to run Docker: {e}")

if __name__ == "__main__":
    inspect_cbomkit()
