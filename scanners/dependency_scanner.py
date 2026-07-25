import os
import re
from typing import List, Dict

class DependencyScanner:
    def __init__(self, target_path: str):
        self.target_path = target_path
        
    def scan(self) -> List[Dict]:
        """
        Scans for dependency files (requirements.txt, pom.xml, go.mod) 
        and extracts libraries that are known to handle cryptography.
        """
        findings = []
        
        for root, _, files in os.walk(self.target_path):
            if "requirements.txt" in files:
                findings.extend(self._parse_requirements_txt(os.path.join(root, "requirements.txt")))
            if "pom.xml" in files:
                findings.extend(self._parse_pom_xml(os.path.join(root, "pom.xml")))
            if "go.mod" in files:
                findings.extend(self._parse_go_mod(os.path.join(root, "go.mod")))
                
        return findings

    def _parse_requirements_txt(self, filepath: str) -> List[Dict]:
        findings = []
        # Sort by length descending so 'pycryptodome' is checked before 'pycrypto'
        crypto_libs = sorted(['cryptography', 'pycrypto', 'pycryptodome', 'passlib', 'bcrypt'], key=len, reverse=True)
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip().lower()
                    for lib in crypto_libs:
                        if line.startswith(lib):
                            v_match = re.search(r'[=><~]+\s*([\w\.\-]+)', line)
                            version = v_match.group(1) if v_match else "unknown"
                            findings.append({
                                "file": filepath,
                                "library": lib,
                                "ecosystem": "python",
                                "raw_entry": line,
                                "version": version,
                                "osv_checked": False # To be integrated with OSV.dev
                            })
                            break # Prevent double matching
        except Exception:
            pass
        return findings

    def _parse_pom_xml(self, filepath: str) -> List[Dict]:
        findings = []
        crypto_libs = ['bouncycastle', 'commons-crypto', 'spring-security-crypto']
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                deps = re.findall(r'<dependency>.*?</dependency>', content, re.DOTALL)
                for dep in deps:
                    dep_lower = dep.lower()
                    for lib in crypto_libs:
                        if lib in dep_lower:
                            v_match = re.search(r'<version>(.*?)</version>', dep)
                            version = v_match.group(1).strip() if v_match else "unknown"
                            findings.append({
                                "file": filepath,
                                "library": lib,
                                "ecosystem": "java",
                                "version": version,
                                "osv_checked": False
                            })
        except Exception:
            pass
        return findings
        
    def _parse_go_mod(self, filepath: str) -> List[Dict]:
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if "golang.org/x/crypto" in line:
                        parts = line.strip().split()
                        version = "unknown"
                        for part in parts:
                            if part.startswith("v"):
                                version = part
                                break
                        findings.append({
                            "file": filepath,
                            "library": "golang.org/x/crypto",
                            "ecosystem": "go",
                            "version": version,
                            "osv_checked": False
                        })
        except Exception:
            pass
        return findings
