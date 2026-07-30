import json
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_corpus():
    config_path = Path("config/repos.json")
    corpus_dir = Path("backend/data/corpus")
    
    if not config_path.exists():
        logging.error(f"Configuration file {config_path} not found.")
        return
        
    corpus_dir.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    repos = config.get("repositories", [])
    if not repos:
        logging.warning("No repositories found in config.")
        return
        
    for repo in repos:
        name = repo["name"]
        url = repo["url"]
        target_path = corpus_dir / name
        
        if target_path.exists():
            logging.info(f"Repository {name} already exists at {target_path}. Resetting to pinned commit if needed.")
            if "commit" in repo:
                try:
                    subprocess.run(["git", "fetch", "--depth", "1", "origin", repo["commit"]], cwd=str(target_path), check=True)
                    subprocess.run(["git", "reset", "--hard", repo["commit"]], cwd=str(target_path), check=True)
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to reset {name} to {repo['commit']}: {e}")
            continue
            
        logging.info(f"Cloning {name} from {url}...")
        try:
            if "commit" in repo:
                # To clone a specific commit, we first init, remote add, fetch depth 1 for the commit, and reset
                target_path.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "init"], cwd=str(target_path), check=True)
                subprocess.run(["git", "remote", "add", "origin", url], cwd=str(target_path), check=True)
                subprocess.run(["git", "fetch", "--depth", "1", "origin", repo["commit"]], cwd=str(target_path), check=True)
                subprocess.run(["git", "reset", "--hard", repo["commit"]], cwd=str(target_path), check=True)
            else:
                subprocess.run(["git", "clone", "--depth", "1", url, str(target_path)], check=True)
            logging.info(f"Successfully cloned {name}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone {name}: {e}")
            
if __name__ == "__main__":
    fetch_corpus()
