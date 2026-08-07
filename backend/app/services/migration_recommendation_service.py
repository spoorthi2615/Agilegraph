from typing import List

from app.models.crypto_asset import AssetType, CryptoAsset
from app.models.migration_recommendation import MigrationRecommendation, Priority


class MigrationRecommendationService:
    """
    Service responsible for analyzing scored cryptographic assets and deterministically
    generating Post-Quantum or classical safe migration recommendations.
    """

    # Deterministic migration mappings
    _MIGRATION_MAP = {
        "MD5": (
            "SHA-256",
            "MD5 is cryptographically broken and vulnerable to collision attacks.",
        ),
        "SHA-1": (
            "SHA-256",
            "SHA-1 is deprecated and vulnerable to collision attacks.",
        ),
        "DES": ("AES-256", "DES uses a 56-bit key which is trivial to brute-force."),
        "3DES": (
            "AES-256",
            "3DES is slow and deprecated. AES-256 is the modern standard.",
        ),
        "DESEDE": (
            "AES-256",
            "DESede (3DES) is deprecated. AES-256 is the modern standard.",
        ),
        "RSA": (
            "ML-KEM",
            "RSA is vulnerable to Shor's algorithm on a quantum computer. ML-KEM is the NIST standard for PQC key encapsulation.",
        ),
        "EC": (
            "ML-DSA (or Hybrid)",
            "Elliptic Curve cryptography is vulnerable to quantum attacks. ML-DSA is the NIST PQC standard for digital signatures.",
        ),
        "ECC": (
            "ML-DSA (or Hybrid)",
            "Elliptic Curve cryptography is vulnerable to quantum attacks. ML-DSA is the NIST PQC standard for digital signatures.",
        ),
    }

    @classmethod
    def generate_recommendations(cls, assets: List[CryptoAsset]) -> List[MigrationRecommendation]:
        """
        Processes a list of scored CryptoAssets and returns actionable migration recommendations.
        """
        recommendations = []
        for asset in assets:
            # We strictly evaluate cryptographic algorithms, not generic software dependencies.
            if asset.asset_type == AssetType.DEPENDENCY:
                continue

            # Ensure the asset has been evaluated by the RiskScoringService
            risk_score = asset.metadata.get("risk_score")
            if risk_score is None or asset.severity is None:
                continue

            algorithm = asset.algorithm.upper() if asset.algorithm else "UNKNOWN"

            # Normalize ECC curve variations (e.g., "ECC (secp256r1)")
            lookup_algo = algorithm
            if lookup_algo.startswith("ECC") or lookup_algo.startswith("EC"):
                lookup_algo = "EC"

            migration_data = cls._MIGRATION_MAP.get(lookup_algo)

            if migration_data:
                recommended_algorithm, rationale = migration_data
            else:
                recommended_algorithm = "Manual Review"
                rationale = f"Algorithm '{algorithm}' requires manual security architecture review."

            priority = cls._determine_priority(risk_score)

            rec = MigrationRecommendation(
                asset_id=asset.asset_id,
                algorithm=algorithm,
                risk_score=risk_score,
                severity=asset.severity,
                recommended_algorithm=recommended_algorithm,
                priority=priority,
                rationale=rationale,
            )
            recommendations.append(rec)

        return recommendations

    @classmethod
    def _determine_priority(cls, risk_score: int) -> Priority:
        """
        Maps a risk score (0-100) mathematically to an actionable migration priority.
        """
        if risk_score >= 90:
            return Priority.IMMEDIATE
        elif risk_score >= 75:
            return Priority.HIGH
        elif risk_score >= 50:
            return Priority.MEDIUM
        else:
            return Priority.LOW
