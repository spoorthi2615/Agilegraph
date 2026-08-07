import logging
from datetime import datetime, timezone
from typing import Optional

from app.scanners.live_tls.tls_certificate import TLSCertificate
from app.scanners.live_tls.tls_finding import TLSFinding

logger = logging.getLogger(__name__)


class TLSScanner:
    """
    Parses raw TLS connection data into strongly typed models and conducts Risk Analysis immutably.
    """

    def parse_der_certificate(self, der_bytes: bytes) -> Optional[TLSCertificate]:
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import ec, rsa

            cert = x509.load_der_x509_certificate(der_bytes, default_backend())

            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.rfc4514_string()
            serial = str(cert.serial_number)
            not_before = (
                cert.not_valid_before_utc.isoformat()
                if hasattr(cert, "not_valid_before_utc")
                else cert.not_valid_before.isoformat()
            )
            not_after = (
                cert.not_valid_after_utc.isoformat()
                if hasattr(cert, "not_valid_after_utc")
                else cert.not_valid_after.isoformat()
            )

            sig_alg = (
                cert.signature_algorithm_oid._name
                if cert.signature_algorithm_oid._name
                else "UNKNOWN"
            )

            pub_key = cert.public_key()
            pub_key_alg = "UNKNOWN"
            key_length = 0

            if isinstance(pub_key, rsa.RSAPublicKey):
                pub_key_alg = "RSA"
                key_length = pub_key.key_size
            elif isinstance(pub_key, ec.EllipticCurvePublicKey):
                pub_key_alg = "ECC"
                key_length = pub_key.curve.key_size

            common_name = "Unknown"
            for attr in cert.subject:
                if attr.oid.dotted_string == "2.5.4.3":  # Common Name OID
                    common_name = str(attr.value)

            san_entries = []
            try:
                ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
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
                fingerprint=fingerprint,
            )
        except ImportError:
            logger.error("cryptography package is required to parse raw DER certificates.")
            return None
        except Exception as e:
            logger.error(f"Failed to parse DER certificate: {e}")
            return None

    def analyze_risk(self, finding: TLSFinding) -> TLSFinding:
        """
        Conducts vulnerability detection.
        Returns a NEW immutable copy of the TLSFinding with risk_score and findings populated.
        """
        new_finding = finding.model_copy(deep=True)
        score = 0.0

        if new_finding.tls_version in ["TLSv1", "TLSv1.1", "SSLv3", "SSLv2"]:
            new_finding.findings.append(
                f"Unsupported/Deprecated Protocol: {new_finding.tls_version}"
            )
            score += 10.0

        if (
            "RC4" in new_finding.cipher_suite
            or "DES" in new_finding.cipher_suite
            or "MD5" in new_finding.cipher_suite
        ):
            new_finding.findings.append(f"Weak Cipher Suite: {new_finding.cipher_suite}")
            score += 8.0

        if new_finding.certificate:
            cert = new_finding.certificate
            try:
                not_after_str = (
                    cert.valid_until.replace("Z", "+00:00")
                    if "Z" in cert.valid_until
                    else cert.valid_until
                )
                not_after = datetime.fromisoformat(not_after_str)
                now = datetime.now(timezone.utc)

                if now > not_after:
                    new_finding.findings.append("Expired certificate")
                    score += 10.0
                elif (not_after - now).days < 30:
                    new_finding.findings.append("Certificate expiring soon (<30 days)")
                    score += 4.0
            except Exception:
                pass

            weak_sigs = ["md5", "sha1"]
            if any(weak in cert.signature_algorithm.lower() for weak in weak_sigs):
                new_finding.findings.append(f"Weak signature algorithm: {cert.signature_algorithm}")
                score += 8.0

            if cert.public_key_algorithm == "RSA" and cert.key_length < 2048:
                new_finding.findings.append(f"Weak RSA key length: {cert.key_length} bits")
                score += 8.0

            if cert.subject == cert.issuer:
                new_finding.findings.append("Self-signed certificate")
                score += 6.0

        new_finding.risk_score = min(score, 10.0)
        return new_finding
