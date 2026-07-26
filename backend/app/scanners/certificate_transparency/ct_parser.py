import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from app.scanners.certificate_transparency.ct_finding import CTFinding

logger = logging.getLogger(__name__)

class CTParser:
    """
    Safely parses JSON responses from crt.sh into CTFinding objects.
    Implements functional immutability during risk evaluation.
    """
    def parse_response(self, domain: str, raw_data: List[Dict[str, Any]]) -> List[CTFinding]:
        findings = []
        if not raw_data:
            return findings
            
        for record in raw_data:
            try:
                cert_id = int(record.get("id", 0))
                issuer = record.get("issuer_name", "UNKNOWN")
                subject = record.get("name_value", "UNKNOWN")
                common_name = record.get("common_name", "UNKNOWN")
                serial = record.get("serial_number", "UNKNOWN")
                not_before = record.get("not_before", "UNKNOWN")
                not_after = record.get("not_after", "UNKNOWN")
                
                # SANs in crt.sh are often separated by newlines in the name_value field
                san_entries = [name.strip() for name in subject.split('\n') if name.strip()]
                
                finding = CTFinding(
                    domain=domain,
                    certificate_id=cert_id,
                    issuer=issuer,
                    subject=subject,
                    common_name=common_name,
                    san_entries=san_entries,
                    serial_number=serial,
                    not_before=not_before,
                    not_after=not_after,
                    certificate_hash=serial # Often crt.sh doesn't provide a direct fingerprint without a secondary lookup
                )
                
                findings.append(finding)
            except Exception as e:
                logger.warning(f"Failed to parse individual crt.sh record: {e}")
                
        return findings
        
    def analyze_risk(self, finding: CTFinding, active_cert_count: int) -> CTFinding:
        """
        Conducts vulnerability detection.
        Returns a NEW immutable copy of the CTFinding with risk_score and findings populated.
        """
        new_finding = finding.model_copy(deep=True)
        score = 0.0
        
        try:
            # Handle crt.sh time format, often like '2023-01-01T00:00:00'
            not_after_str = new_finding.not_after
            if not_after_str.endswith("Z"):
                not_after_str = not_after_str.replace("Z", "+00:00")
            elif "+" not in not_after_str and "-" not in not_after_str[10:]:
                # If no timezone info, assume UTC
                not_after_str += "+00:00"
                
            not_after = datetime.fromisoformat(not_after_str)
            now = datetime.now(timezone.utc)
            
            # Since crt.sh is historical, expired certs aren't necessarily a critical risk,
            # they are just historical logs. But we flag them.
            if now > not_after:
                new_finding.findings.append("Historically Expired Certificate")
                # Lower penalty since it's just a historical artifact
                score += 1.0
            else:
                new_finding.findings.append("Active Certificate")
                
                # If there are many ACTIVE certificates simultaneously, it might indicate rogue issuance
                if active_cert_count > 3:
                    new_finding.findings.append(f"High number of active certificates detected ({active_cert_count}). Potential rogue issuance or misconfiguration.")
                    score += 6.0
                    
        except Exception:
            pass
            
        if "Let's Encrypt" not in new_finding.issuer and "DigiCert" not in new_finding.issuer and "GlobalSign" not in new_finding.issuer:
             # Heuristic for unexpected/unknown issuers
             new_finding.findings.append(f"Uncommon Issuer detected: {new_finding.issuer}")
             score += 3.0
             
        new_finding.risk_score = min(score, 10.0)
        return new_finding
