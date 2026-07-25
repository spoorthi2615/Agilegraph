import subprocess
import json
import os
from typing import List, Dict

class CodeScanner:
    def __init__(self, target_path: str):
        self.target_path = target_path

    def run_scan(self) -> List[Dict]:
        """
        Runs Semgrep using standard insecure cryptography rules.
        Returns a list of findings.
        """
        if not os.path.exists(self.target_path):
            raise FileNotFoundError(f"Target path {self.target_path} does not exist.")
            
        print(f"Running Semgrep on {self.target_path}...")
        
        # Using built-in security rules for multiple languages focusing on crypto
        cmd = [
            "semgrep",
            "scan",
            "--config", "p/security-audit",
            "--config", "p/secrets",
            "--json",
            self.target_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # Surface Semgrep execution errors explicitly (e.g. failing to download configs)
        if result.returncode != 0:
            raise RuntimeError(f"Semgrep failed (exit code {result.returncode}). Stderr: {result.stderr}")
        if "403" in result.stderr or "failed to download" in result.stderr.lower():
            raise RuntimeError(f"Semgrep failed to download rulesets. Network blocked or unauthenticated. Stderr: {result.stderr}")
        elif "error" in result.stderr.lower() or "failed" in result.stderr.lower():
            print(f"Warning: Semgrep reported issues: {result.stderr}")
            
        if not result.stdout:
            return []
            
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Semgrep returned invalid JSON: {e}")
            
        findings = []
        
        for match in data.get('results', []):
            # Filter for crypto-related findings
            check_id = match['check_id'].lower()
            filter_kws = ['crypto', 'cipher', 'md5', 'sha1', 'sha-1', 'des', 'rc4', 'rsa', 'ecc', 'ecdsa', 'dsa', 'aes', 'chacha']
            if any(kw in check_id for kw in filter_kws):
                
                algorithm_label = "UNKNOWN"
                if "md5" in check_id: algorithm_label = "MD5"
                elif "sha1" in check_id or "sha-1" in check_id: algorithm_label = "SHA1"
                elif "des" in check_id: algorithm_label = "DES"
                elif "rc4" in check_id: algorithm_label = "RC4"
                elif "rsa" in check_id: algorithm_label = "RSA"
                elif "ecc" in check_id or "ecdsa" in check_id: algorithm_label = "ECC"
                elif "dsa" in check_id: algorithm_label = "DSA"
                elif "aes" in check_id: algorithm_label = "AES"
                elif "chacha" in check_id: algorithm_label = "CHACHA20"
                
                findings.append({
                    "file": match['path'],
                    "line": match['start']['line'],
                    "algorithm_hint": match['check_id'],
                    "algorithm": algorithm_label,
                    "snippet": match['extra']['lines'],
                    "message": match['extra']['message']
                })
                
        return findings

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        scanner = CodeScanner(sys.argv[1])
        print(json.dumps(scanner.run_scan(), indent=2))
