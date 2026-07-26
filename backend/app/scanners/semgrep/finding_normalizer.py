from typing import List, Dict, Any
from app.scanners.semgrep.semgrep_finding import SemgrepFinding

class FindingNormalizer:
    """
    Merges Semgrep findings with existing custom scanner findings, identifying and deduplicating overlaps.
    """
    @staticmethod
    def normalize(custom_findings: List[Dict[str, Any]], semgrep_findings: List[SemgrepFinding]) -> List[Dict[str, Any]]:
        """
        Takes dictionaries representing existing nodes and new Semgrep findings.
        Returns a unified list of finding dictionaries, annotated with their source attribution.
        """
        normalized = []
        custom_index = {}
        
        for cf in custom_findings:
            cf_key = (cf.get("file_path", ""), cf.get("line", 0))
            if "source" not in cf:
                cf["source"] = "Custom"
            custom_index[cf_key] = cf
            
        for sf in semgrep_findings:
            sf_key = (sf.file_path, sf.line)
            
            if sf_key in custom_index:
                # Deduplicate: We already have a custom finding here.
                # Update the source attribution to show both engines found it.
                existing = custom_index[sf_key]
                existing["source"] = "Both"
                existing["semgrep_rule_id"] = sf.rule_id
            else:
                # Unique Semgrep finding
                new_finding = {
                    "rule_id": sf.rule_id,
                    "severity": sf.severity,
                    "message": sf.message,
                    "language": sf.language,
                    "file_path": sf.file_path,
                    "line": sf.line,
                    "column": sf.column,
                    "source": "Semgrep"
                }
                normalized.append(new_finding)
                
        # Combine the original custom findings (some may be updated to "Both") and new unique Semgrep findings
        return list(custom_index.values()) + normalized
