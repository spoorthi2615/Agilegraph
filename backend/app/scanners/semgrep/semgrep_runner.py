import logging
import subprocess
import json
from typing import Dict, Any, Optional
from app.scanners.semgrep.semgrep_config import SemgrepConfig

logger = logging.getLogger(__name__)

class SemgrepRunner:
    """
    Safely orchestrates the execution of the Semgrep CLI, returning the raw JSON output.
    Gracefully degrades if the CLI is not available.
    """
    def __init__(self, config: SemgrepConfig):
        self.config = config
        
    def execute(self, target_directory: str) -> Optional[Dict[str, Any]]:
        """
        Executes semgrep on the target directory and returns the parsed JSON output.
        Returns None if execution fails or times out.
        """
        cmd = ["semgrep", "scan", "--json"]
        
        if self.config.custom_rules_dir:
            cmd.extend(["--config", self.config.custom_rules_dir])
        elif self.config.use_default_rules:
            cmd.extend(["--config", "auto"])
            
        for ext in self.config.exclude_dirs:
            cmd.extend(["--exclude", ext])
            
        cmd.append(target_directory)
        
        try:
            # We don't want to crash if Semgrep isn't installed, as this is an optional supplementary scanner
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            # Semgrep returns 1 if findings were found, which is a success for us.
            if result.returncode not in [0, 1]:
                logger.error(f"Semgrep CLI error (code {result.returncode}): {result.stderr}")
                return None
                
            return json.loads(result.stdout)
            
        except FileNotFoundError:
            logger.warning("Semgrep CLI not found in PATH. Skipping Semgrep analysis.")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Semgrep execution timed out after {self.config.timeout_seconds} seconds.")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode Semgrep JSON output: {e}")
            return None
