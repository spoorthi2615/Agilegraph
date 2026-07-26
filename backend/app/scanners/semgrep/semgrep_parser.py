import os
import json
import logging
from typing import List, Optional
from app.scanners.semgrep.semgrep_finding import SemgrepFinding

logger = logging.getLogger(__name__)

class SemgrepParser:
    """
    Safely parses JSON output from Semgrep temp files into strongly typed SemgrepFinding objects.
    """
    def parse_file(self, file_path: str) -> List[SemgrepFinding]:
        findings = []
        if not file_path or not os.path.exists(file_path):
            return findings
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_output = json.load(f)
                
            if not raw_output or "results" not in raw_output:
                logger.warning("Semgrep output missing 'results' block.")
                return findings
                
            for res in raw_output["results"]:
                try:
                    rule_id = res.get("check_id", "unknown_rule")
                    extra = res.get("extra", {})
                    
                    severity = extra.get("severity", "UNKNOWN")
                    message = extra.get("message", "No message provided")
                    metadata = extra.get("metadata", {})
                    
                    file_path_node = res.get("path", "")
                    start = res.get("start", {})
                    line = start.get("line", 0)
                    column = start.get("col", 0)
                    
                    code_snippet = extra.get("lines", "").strip()
                    
                    language = "unknown"
                    if file_path_node:
                        if file_path_node.endswith(".py"): language = "python"
                        elif file_path_node.endswith(".java"): language = "java"
                        elif file_path_node.endswith(".go"): language = "go"
                        elif file_path_node.endswith(".ts") or file_path_node.endswith(".js"): language = "javascript"
                    
                    finding = SemgrepFinding(
                        rule_id=rule_id,
                        severity=severity,
                        message=message,
                        language=language,
                        file_path=file_path_node,
                        line=line,
                        column=column,
                        code_snippet=code_snippet,
                        metadata=metadata,
                        source="Semgrep"
                    )
                    findings.append(finding)
                except Exception as e:
                    logger.warning(f"Failed to parse individual Semgrep result: {e}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON output from Semgrep: {e}")
        except OSError as e:
            logger.error(f"Filesystem error parsing Semgrep output: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Semgrep JSON parsing: {e}")
        finally:
            # Always delete the temporary file after parsing to prevent disk exhaustion
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    logger.warning(f"Failed to delete Semgrep temp file: {file_path}")
                    
        return findings
