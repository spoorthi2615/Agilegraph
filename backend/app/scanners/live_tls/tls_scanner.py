import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.scanners.live_tls.tls_certificate import TLSCertificate
from app.scanners.live_tls.tls_finding import TLSFinding

logger = logging.getLogger(__name__)

class TLSScanner:
    """
    Parses raw TLS connection data into strongly typed models and conducts Risk Analysis.
    """
    def __init__(self):
        pass
        
    def parse_der_certificate(self, der_bytes: bytes) -> Optional[TLSCertificate]:
        """
        Parses a raw DER encoded certificate into our strongly typed Pydantic model
        using the cryptography library (AgileGraph standard dependency).
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.asymmetric import rsa, ec
            from cryptography.hazmat.primitives import hashes
            
            cert = x509.load_der_x509_certificate(der_bytes, default_backend())
            
            # Extract basic data safely depending on cryptography version
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            serial = str(cert.serial_number)
            not_before = cert.not_valid_before_utc.isoformat() if hasattr(cert, 'not_valid_before_utc') else cert.not_valid_before.isoformat()
            not_after = cert.not_valid_after_utc.isoformat() if hasattr(cert, 'not_valid_after_utc') else cert.not_valid_after.isoformat()
            
            # Algorithms
            sig_alg = cert.signature_algorithm_oid._name if cert.signature_algorithm_oid._name else "UNKNOWN"
            
            pub_key = cert.public_key()
            pub_key_alg = "UNKNOWN"
            key_length = 0
            
            if isinstance(pub_key, rsa.RSAPublicKey):
                pub_key_alg = "RSA"
                key_length = pub_key.key_size
            elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                pub_key_alg = "ECC"
                key_length = pub_key.curve.key_size
                
            # SAN and Common Name
            common_name = "Unknown"
            for attr in cert.subject:
                if attr.oid.dotted_string == "2.5.4.3": # Common Name OID
                    common_name = str(attr.value)
                    
            san_entries = []
            try:
                ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                # We extract dns names, ip addresses, etc. For simplicity, just get string representations
                san_entries = [str(name.value) for name in ext.value]
            except x509.ExtensionNotFound:
                pass
                
            fingerprint = cert.fingerprint(hashes.SHA256()).hex()
            
            return TLSCertificate(
                subject=subject,
                issuer=issuer,
                serial_number=serial,
                valid_from=not_before,
                valid_until=not_after,
                signature_algorithm=sig_alg,
                public_key_algorithm=pub_key_alg,
                key_length=key_length,
                san_entries=san_entries,
                common_name=common_name,
                fingerprint=fingerprint
            )
        except ImportError:
            logger.error("cryptography package is required to parse raw DER certificates.")
            return None
        except Exception as e:
            logger.error(f"Failed to parse DER certificate: {e}")
            return None
            
    def analyze_risk(self, finding: TLSFinding):
        """
        Conducts vulnerability and risk detection on the collected TLS metadata.
        Populates finding.risk_score and finding.findings.
        """
        score = 0.0
        
        # 1. Check Protocol Version
        if finding.tls_version in ["TLSv1", "TLSv1.1", "SSLv3", "SSLv2"]:
            finding.findings.append(f"Unsupported/Deprecated Protocol: {finding.tls_version}")
            score += 10.0
            
        # 2. Check Cipher Suite
        if "RC4" in finding.cipher_suite or "DES" in finding.cipher_suite or "MD5" in finding.cipher_suite:
            finding.findings.append(f"Weak Cipher Suite: {finding.cipher_suite}")
            score += 8.0
            
        if finding.certificate:
            cert = finding.certificate
            
            # 3. Check Expiry
            try:
                # Ensure UTC offset parsing is standard
                not_after_str = cert.valid_until.replace("Z", "+00:00") if "Z" in cert.valid_until else cert.valid_until
                not_after = datetime.fromisoformat(not_after_str)
                now = datetime.now(timezone.utc)
                
                if now > not_after:
                    finding.findings.append("Expired certificate")
                    score += 10.0
                elif (not_after - now).days < 30:
                    finding.findings.append("Certificate expiring soon (<30 days)")
                    score += 4.0
            except Exception as e:
                logger.warning(f"Failed to parse certificate expiry for risk analysis: {e}")
                
            # 4. Check Weak Signature Algorithm
            weak_sigs = ["md5", "sha1"]
            if any(weak in cert.signature_algorithm.lower() for weak in weak_sigs):
                finding.findings.append(f"Weak signature algorithm: {cert.signature_algorithm}")
                score += 8.0
                
            # 5. Check Key Strength
            if cert.public_key_algorithm == "RSA" and cert.key_length < 2048:
                finding.findings.append(f"Weak RSA key length: {cert.key_length} bits")
                score += 8.0
                
            # 6. Check Self-Signed
            if cert.subject == cert.issuer:
                finding.findings.append("Self-signed certificate")
                score += 6.0
                
        finding.risk_score = min(score, 10.0)
