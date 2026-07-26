import logging
from typing import Dict, Any, List
from app.scanners.semgrep.semgrep_finding import SemgrepFinding

logger = logging.getLogger(__name__)

class SemgrepParser:
    """
    Parses the raw JSON output from Semgrep into strongly typed SemgrepFinding objects.
    """
    @staticmethod
    def parse(raw_output: Dict[str, Any]) -> List[SemgrepFinding]:
        findings = []
        if not raw_output or "results" not in raw_output:
            return findings
            
        for res in raw_output["results"]:
            try:
                rule_id = res.get("check_id", "unknown_rule")
                extra = res.get("extra", {})
                
                # Extract severity and message
                severity = extra.get("severity", "UNKNOWN")
                message = extra.get("message", "No message provided")
                metadata = extra.get("metadata", {})
                
                # Extract location data
                file_path = res.get("path", "")
                start = res.get("start", {})
                line = start.get("line", 0)
                column = start.get("col", 0)
                
                code_snippet = extra.get("lines", "").strip()
                
                # Map language by checking the file extension if available, else 'unknown'
                language = "unknown"
                if file_path:
                    if file_path.endswith(".py"): language = "python"
                    elif file_path.endswith(".java"): language = "java"
                    elif file_path.endswith(".go"): language = "go"
                    elif file_path.endswith(".ts") or file_path.endswith(".js"): language = "javascript"
                
                finding = SemgrepFinding(
                    rule_id=rule_id,
                    severity=severity,
                    message=message,
                    language=language,
                    file_path=file_path,
                    line=line,
                    column=column,
                    code_snippet=code_snippet,
                    metadata=metadata
                )
                findings.append(finding)
            except Exception as e:
                logger.warning(f"Failed to parse a Semgrep result: {e}")
                
        return findings
