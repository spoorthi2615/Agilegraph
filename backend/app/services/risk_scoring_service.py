from typing import List, Optional

from app.models.crypto_asset import CryptoAsset, AssetType, Severity

from app.models.risk_policy import RiskPolicy

class RiskScoringService:
    """
    Evaluates discovered cryptographic assets and assigns a deterministic 
    risk score and severity level based on an injected RiskPolicy.
    """

    @classmethod
    def score_assets(cls, assets: List[CryptoAsset], policy: Optional[RiskPolicy] = None) -> List[CryptoAsset]:
        """
        Iterates over a list of CryptoAssets, calculates a risk score for each,
        assigns the appropriate Severity enum, and embeds the score in the metadata.
        Returns the modified list of assets.
        """
        if policy is None:
            policy = RiskPolicy.default()
            
        for asset in assets:
            score = cls._calculate_score(asset, policy)
            
            # Embed the numeric score for precise querying
            if asset.metadata is None:
                asset.metadata = {}
            asset.metadata["risk_score"] = score
            
            # Assign the severity bucket
            asset.severity = cls._determine_severity(score)
            
        return assets

    @classmethod
    def _calculate_score(cls, asset: CryptoAsset, policy: RiskPolicy) -> int:
        """
        Determines the numeric risk score using deterministic rules from the injected policy.
        """
        if asset.asset_type == AssetType.DEPENDENCY:
            return policy.dependency_baseline_score
            
        if not asset.algorithm:
            return policy.unknown_baseline_score
            
        # Upper case matching for robust lookup
        algo = asset.algorithm.upper()
        
        # Handle ECC curve variations (e.g., "ECC (secp256r1)") by extracting base name
        if algo.startswith("ECC") or algo.startswith("EC"):
            return policy.algorithm_scores.get("EC", 40)
            
        return policy.algorithm_scores.get(algo, policy.unknown_baseline_score)

    @classmethod
    def _determine_severity(cls, score: int) -> Severity:
        """
        Maps a numeric risk score (0-100) to a standard Severity enum.
        """
        if score <= 25:
            return Severity.LOW
        elif score <= 50:
            return Severity.MEDIUM
        elif score <= 75:
            return Severity.HIGH
        else:
            return Severity.CRITICAL
