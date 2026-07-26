import logging
import json
import urllib.request
import urllib.error
import time
from typing import List, Dict, Any, Optional
from app.scanners.certificate_transparency.ct_config import CTConfig

logger = logging.getLogger(__name__)

class CTClient:
    """
    Passive OSINT client for querying the crt.sh Certificate Transparency logs.
    Implements rate limiting and exponential backoff.
    """
    def __init__(self, config: CTConfig):
        self.config = config
        
    def query_domain(self, domain: str, include_wildcards: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Queries crt.sh for the given domain.
        Returns the parsed JSON response array or None on failure.
        """
        query_domain = f"%.{domain}" if include_wildcards else domain
        url = f"{self.config.crt_sh_base_url}?q={query_domain}&output=json"
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                logger.info(f"Querying Certificate Transparency (crt.sh) for {query_domain} (Attempt {attempt}/{self.config.max_retries})")
                
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'AgileGraph-CT-Scanner/1.0'}
                )
                
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                    if response.status == 200:
                        data = response.read().decode('utf-8')
                        if not data:
                            return []
                        return json.loads(data)
                        
            except urllib.error.HTTPError as e:
                logger.warning(f"crt.sh HTTP error: {e.code} - {e.reason}")
                if e.code in [502, 503, 504, 429]:
                    # Rate limited or service unavailable, backoff and retry
                    pass
                else:
                    break # Don't retry 404s or 400s
            except urllib.error.URLError as e:
                logger.warning(f"crt.sh URL error: {e.reason}")
            except json.JSONDecodeError as e:
                logger.error(f"crt.sh returned malformed JSON: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected network error querying crt.sh: {e}")
                
            if attempt < self.config.max_retries:
                sleep_time = self.config.backoff_factor ** attempt
                logger.info(f"Backing off for {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
                
        logger.error(f"Failed to retrieve CT logs for {domain} after {self.config.max_retries} attempts.")
        return None
