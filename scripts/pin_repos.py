import json
import subprocess
from pathlib import Path

def pin_commits():
    config_path = Path("config/repos.json")
    if not config_path.exists():
        print("config/repos.json not found!")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    for repo in config.get("repositories", []):
        if "commit" not in repo:
            try:
                out = subprocess.check_output(["git", "ls-remote", repo["url"], "HEAD"]).decode("utf-8")
                commit_hash = out.split()[0]
                repo["commit"] = commit_hash
                print(f"Pinned {repo['name']} to {commit_hash}")
            except Exception as e:
                print(f"Error fetching commit for {repo['name']}: {e}")

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print("Finished updating config/repos.json with pinned commits.")

if __name__ == "__main__":
    pin_commits()
