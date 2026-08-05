import ssl
import socket
from typing import Dict, Any, List
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa

class CertificateParsingService:
    @staticmethod
    def parse_certificate_bytes(cert_bytes: bytes) -> Dict[str, Any]:
        """
        Parses raw certificate bytes and extracts key cryptographic properties
        for PQC readiness scoring.
        """
        try:
            cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
        except ValueError:
            # Try DER format if PEM fails
            cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
            
        public_key = cert.public_key()
        algorithm_name = "Unknown"
        key_size = 0
        
        if isinstance(public_key, rsa.RSAPublicKey):
            algorithm_name = "RSA"
            key_size = public_key.key_size
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            algorithm_name = "ECDSA"
            key_size = public_key.key_size
        elif isinstance(public_key, dsa.DSAPublicKey):
            algorithm_name = "DSA"
            key_size = public_key.key_size
            
        subject = cert.subject.rfc4514_string()
        issuer = cert.issuer.rfc4514_string()
        
        try:
            not_before = cert.not_valid_before_utc.isoformat()
            not_after = cert.not_valid_after_utc.isoformat()
        except AttributeError:
            # For older cryptography versions
            not_before = cert.not_valid_before.isoformat()
            not_after = cert.not_valid_after.isoformat()
        
        return {
            "algorithm": algorithm_name,
            "key_size": key_size,
            "subject": subject,
            "issuer": issuer,
            "not_before": not_before,
            "not_after": not_after,
            # Standard x509 are not PQC safe yet unless Dilithium/Sphincs+
            "is_pqc_safe": False,
        }

class TLSScanningService:
    @staticmethod
    def scan_domain(domain: str, port: int = 443) -> List[Dict[str, Any]]:
        """
        Connects to a domain and extracts the TLS certificate chain.
        Returns parsed certificate metadata.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        # We just want to extract, not validate trust
        context.verify_mode = ssl.CERT_NONE
        
        parsed_certs = []
        try:
            with socket.create_connection((domain, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    # Retrieve the binary certificate
                    cert_der = ssock.getpeercert(binary_form=True)
                    if cert_der:
                        parsed = CertificateParsingService.parse_certificate_bytes(cert_der)
                        parsed['source'] = f"{domain}:{port}"
                        parsed_certs.append(parsed)
        except Exception as e:
            raise RuntimeError(f"Failed to scan {domain}:{port} - {str(e)}")
            
        return parsed_certs
