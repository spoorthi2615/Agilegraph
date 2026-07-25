import ssl
import socket
import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from typing import Dict

class CertificateScanner:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def scan_endpoint(self, hostname: str, port: int = 443) -> Dict:
        """
        Fetches the SSL/TLS certificate for a given endpoint.
        Returns details about the certificate including algorithm and expiry.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        try:
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    x509_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    
                    # Parse using cryptography library
                    crypto_cert = x509.load_pem_x509_certificate(x509_pem.encode('utf-8'), default_backend())
                    
                    public_key = crypto_cert.public_key()
                    
                    algorithm = "UNKNOWN"
                    key_size = 0
                    
                    from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa, ed25519, ed448
                    
                    if isinstance(public_key, rsa.RSAPublicKey):
                        algorithm = "RSA"
                        key_size = public_key.key_size
                    elif isinstance(public_key, ec.EllipticCurvePublicKey):
                        algorithm = "ECC"
                        key_size = public_key.curve.key_size
                    elif isinstance(public_key, dsa.DSAPublicKey):
                        algorithm = "DSA"
                        key_size = public_key.key_size
                    elif isinstance(public_key, ed25519.Ed25519PublicKey):
                        algorithm = "EdDSA"
                        key_size = 256
                    elif isinstance(public_key, ed448.Ed448PublicKey):
                        algorithm = "EdDSA"
                        key_size = 448
                        
                    try:
                        expiry_date = crypto_cert.not_valid_after_utc
                    except AttributeError:
                        expiry_date = crypto_cert.not_valid_after
                    
                    return {
                        "endpoint": f"{hostname}:{port}",
                        "status": "success",
                        "raw_pem": x509_pem,
                        "algorithm": algorithm,
                        "key_size": key_size,
                        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                        "signature_algorithm": crypto_cert.signature_hash_algorithm.name if crypto_cert.signature_hash_algorithm else "UNKNOWN"
                    }
        except Exception as e:
            return {
                "endpoint": f"{hostname}:{port}",
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        scanner = CertificateScanner()
        print(scanner.scan_endpoint(sys.argv[1]))
