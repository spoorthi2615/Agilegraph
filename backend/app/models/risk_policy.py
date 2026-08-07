from typing import Dict

from pydantic import BaseModel, Field


class RiskPolicy(BaseModel):
    """
    Domain model encapsulating the enterprise risk configuration for cryptographic assets.
    Defines baseline scoring rules independent of the calculation engine.
    """

    algorithm_scores: Dict[str, int] = Field(
        default_factory=lambda: {
            "MD5": 95,
            "SHA-1": 85,
            "SHA-256": 20,
            "DES": 95,
            "3DES": 75,
            "DESede": 75,
            "AES": 20,
            "RSA": 70,
            "EC": 40,
            "ECC": 40,
        }
    )

    dependency_baseline_score: int = 30
    unknown_baseline_score: int = 50
    cvss_weight_multiplier: float = 3.0

    @classmethod
    def default(cls) -> "RiskPolicy":
        """
        Returns the standard default risk policy.
        """
        return cls()
