import logging
from typing import List, Optional
from datetime import datetime, timezone
from app.scanners.certificate_transparency.ct_client import CTClient
from app.scanners.certificate_transparency.ct_parser import CTParser
from app.scanners.certificate_transparency.ct_finding import CTFinding

logger = logging.getLogger(__name__)

class CTService:
    """
    Facade orchestrator for the Certificate Transparency integration.
    Utilizes strict Dependency Injection to remain decoupled.
    """
    def __init__(self, client: CTClient, parser: CTParser):
        self.client = client
        self.parser = parser
        
    def scan_domain(self, domain: str, include_wildcards: bool = True) -> List[CTFinding]:
        """
        Executes a passive CT log query against the target domain.
        Returns a strongly typed list of historical CTFindings, ready for Graph Integration.
        """
        raw_data = self.client.query_domain(domain, include_wildcards)
        
        if raw_data is None:
            logger.warning(f"CT Client failed to return data for {domain}.")
            return []
            
        findings = self.parser.parse_response(domain, raw_data)
        logger.info(f"CT Parser generated {len(findings)} base historical findings.")
        
        # Determine the number of currently active certificates in this batch
        active_cert_count = 0
        now = datetime.now(timezone.utc)
        
        for f in findings:
            try:
                not_after_str = f.not_after
                if not_after_str.endswith("Z"):
                    not_after_str = not_after_str.replace("Z", "+00:00")
                elif "+" not in not_after_str and "-" not in not_after_str[10:]:
                    not_after_str += "+00:00"
                    
                not_after = datetime.fromisoformat(not_after_str)
                if now <= not_after:
                    active_cert_count += 1
            except Exception:
                pass
                
        # Run Risk detection immutably
        enriched_findings = []
        for finding in findings:
            enriched = self.parser.analyze_risk(finding, active_cert_count)
            enriched_findings.append(enriched)
            
        # Deduplicate based on exact serial number to avoid blowing up the graph with 
        # identical certs submitted to multiple logs
        deduped = {}
        for f in enriched_findings:
            if f.serial_number not in deduped:
                deduped[f.serial_number] = f
                
        final_list = list(deduped.values())
        logger.info(f"CT Scan complete. Returning {len(final_list)} unique certificates ({active_cert_count} currently active).")
        return final_list
