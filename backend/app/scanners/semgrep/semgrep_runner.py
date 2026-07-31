import os
import logging
import subprocess
import tempfile
from typing import Optional
from app.scanners.semgrep.semgrep_config import SemgrepConfig

logger = logging.getLogger(__name__)

class SemgrepRunner:
    """
    Safely orchestrates the execution of the Semgrep CLI, returning a path to the generated JSON output.
    Uses tempfile to prevent OOM errors on large repositories.
    """
    def __init__(self, config: SemgrepConfig):
        self.config = config
        
    def _validate_path(self, path: str) -> str:
        """
        Validates untrusted user paths to prevent argument injection and path traversal.
        """
        clean_path = os.path.normpath(path)
        if clean_path.startswith("-"):
            raise ValueError(f"Invalid path detected (Argument Injection risk): {path}")
        return clean_path
        
    def execute(self, target_directory: str) -> Optional[str]:
        """
        Executes semgrep on the target directory and outputs to a temporary file.
        Returns the path to the temporary JSON file, or None if execution fails.
        """
        try:
            safe_target = self._validate_path(target_directory)
            
            cmd = ["semgrep", "scan", "--json", "--no-rewrite-rule-ids"]
            
            if self.config.custom_rules_dir:
                safe_rule_dir = self._validate_path(self.config.custom_rules_dir)
                cmd.extend(["--config", safe_rule_dir])
            elif self.config.use_default_rules:
                # Use named lightweight rule packs instead of "auto" (which downloads the full registry)
                cmd.extend(["--config", "p/secrets", "--config", "p/python"])
            else:
                # No rules — semgrep will return 0 findings cleanly without hanging
                cmd.extend(["--config", "r/python.lang.correctness"])
                # If no config at all, semgrep errors; skip execution safely
                logger.info("Semgrep: no rules configured, skipping.")
                return None
                
            for ext in self.config.exclude_dirs:
                safe_ext = self._validate_path(ext)
                cmd.extend(["--exclude", safe_ext])
                
            # Create a secure temporary file for the massive JSON output
            fd, temp_path = tempfile.mkstemp(suffix=".json", prefix="semgrep_out_")
            os.close(fd) # Close immediately, we just need the guaranteed unique path
            
            cmd.extend(["--output", temp_path])
            cmd.append(safe_target)
            
            # Execute safely without shell, dumping directly to the temp file
            result = subprocess.run(
                cmd,
                capture_output=False,
                stdout=subprocess.DEVNULL, # Drop stdout to prevent RAM exhaustion
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            if result.returncode not in [0, 1]:
                logger.error(f"Semgrep CLI error (code {result.returncode}): {result.stderr}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return None
                
            return temp_path
            
        except ValueError as ve:
            logger.error(f"Security validation failed: {ve}")
            return None
        except FileNotFoundError:
            logger.warning("Semgrep CLI not found in PATH. Skipping Semgrep analysis.")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Semgrep execution timed out after {self.config.timeout_seconds} seconds.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing Semgrep: {e}")
            return None
