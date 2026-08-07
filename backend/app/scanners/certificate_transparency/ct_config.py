from pydantic import BaseModel, Field


class CTConfig(BaseModel):
    """
    Configuration for the Certificate Transparency OSINT Client.
    """

    crt_sh_base_url: str = Field(default="https://crt.sh/")
    timeout_seconds: float = Field(default=15.0)
    max_retries: int = Field(default=3)
    backoff_factor: float = Field(default=1.5)
