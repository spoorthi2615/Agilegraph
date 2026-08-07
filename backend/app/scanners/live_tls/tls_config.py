from pydantic import BaseModel, Field


class TLSConfig(BaseModel):
    """
    Configuration for Live TLS network scanning.
    """

    default_port: int = Field(default=443)
    timeout_seconds: float = Field(default=5.0)
    verify_hostname: bool = Field(default=True)

    # If False, grabs cert even if expired, self-signed, or untrusted by system roots.
    # Crucial for security auditing where we WANT to detect broken certs without crashing the handshake.
    validate_certificate: bool = Field(default=False)
