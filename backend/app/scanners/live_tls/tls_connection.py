import ssl
import socket
import logging
from typing import Tuple, Optional
from app.scanners.live_tls.tls_config import TLSConfig

logger = logging.getLogger(__name__)

class TLSConnectionManager:
    """
    Manages raw socket creation and SSL context wrapping for retrieving live TLS data.
    """
    def __init__(self, config: TLSConfig):
        self.config = config
        
        # Create an SSL context
        self.context = ssl.create_default_context()
        
        # Security auditing bypasses: We want to connect even if the cert is expired/invalid
        # so we can parse and analyze WHY it is invalid.
        if not self.config.validate_certificate:
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE
        elif not self.config.verify_hostname:
            self.context.check_hostname = False
            
    def get_live_connection_data(self, domain: str, port: int) -> Tuple[Optional[bytes], Optional[ssl.SSLSocket]]:
        """
        Attempts a TLS handshake with the target domain.
        Returns the raw binary DER certificate bytes and the active socket for protocol analysis.
        """
        logger.info(f"Initiating TLS connection to {domain}:{port}...")
        
        try:
            # Create standard socket with exact timeout bounds
            sock = socket.create_connection((domain, port), timeout=self.config.timeout_seconds)
            
            # Wrap the socket in the configured TLS context
            ssock = self.context.wrap_socket(sock, server_hostname=domain if self.config.verify_hostname else None)
            
            # Because CERT_NONE causes Python's getpeercert() to return an empty dict,
            # we MUST request the binary DER form to parse it ourselves.
            der_bytes = ssock.getpeercert(binary_form=True)
            
            return der_bytes, ssock
            
        except socket.timeout:
            logger.error(f"Connection to {domain}:{port} timed out after {self.config.timeout_seconds}s.")
            return None, None
        except socket.gaierror:
            logger.error(f"DNS Resolution failed for {domain}.")
            return None, None
        except ssl.SSLError as e:
            logger.error(f"SSL Handshake failed for {domain}: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected network error connecting to {domain}: {e}")
            return None, None
