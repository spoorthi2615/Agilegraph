import ipaddress
import logging
import socket
import ssl
from typing import Optional, Tuple

from app.scanners.live_tls.tls_config import TLSConfig

logger = logging.getLogger(__name__)


class TLSConnectionManager:
    """
    Manages raw socket creation and SSL context wrapping for retrieving live TLS data.
    Implements strict SSRF protection to prevent unauthorized internal network scanning.
    """

    def __init__(self, config: TLSConfig):
        self.config = config

        self.context = ssl.create_default_context()

        if not self.config.validate_certificate:
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE
        elif not self.config.verify_hostname:
            self.context.check_hostname = False

    def _validate_ssrf_safety(self, domain: str) -> bool:
        """
        Resolves the domain and ensures it does not map to a private/internal IP address.
        """
        try:
            ip = socket.gethostbyname(domain)
            ip_obj = ipaddress.ip_address(ip)

            # Block Loopback (127.0.0.1), Private (10.x, 192.168.x), Link-Local (169.254.x.x)
            if (
                ip_obj.is_loopback
                or ip_obj.is_private
                or ip_obj.is_link_local
                or ip_obj.is_reserved
            ):
                return False
            return True
        except socket.gaierror:
            return False  # Unresolvable domains are inherently unsafe to scan

    def get_live_connection_data(
        self, domain: str, port: int
    ) -> Tuple[Optional[bytes], Optional[ssl.SSLSocket]]:
        """
        Attempts a TLS handshake with the target domain.
        Returns the raw binary DER certificate bytes and the active socket for protocol analysis.
        """
        if not self._validate_ssrf_safety(domain):
            logger.error(
                f"SSRF Violation Blocked: Target {domain} resolved to a prohibited internal or unresolvable IP."
            )
            return None, None

        logger.info(f"Initiating TLS connection to {domain}:{port}...")

        try:
            sock = socket.create_connection((domain, port), timeout=self.config.timeout_seconds)
            ssock = self.context.wrap_socket(
                sock, server_hostname=domain if self.config.verify_hostname else None
            )

            der_bytes = ssock.getpeercert(binary_form=True)
            return der_bytes, ssock

        except socket.timeout:
            logger.error(f"Connection to {domain}:{port} timed out.")
            return None, None
        except ssl.SSLError as e:
            logger.error(f"SSL Handshake failed for {domain}: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected network error connecting to {domain}: {e}")
            return None, None
