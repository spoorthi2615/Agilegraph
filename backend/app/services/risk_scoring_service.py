from typing import List, Dict, Optional

from app.models.crypto_asset import CryptoAsset, AssetType, Severity

class RiskScoringService:
    """
    Evaluates discovered cryptographic assets and assigns a deterministic 
    risk score and severity level based on established security baselines.
    """

    # Scoring mappings based on algorithm
    # Note: ECC is sometimes detected as "ECC" or "EC" depending on the scanner
    _ALGORITHM_SCORES: Dict[str, int] = {
        # Hash
        "MD5": 95,
        "SHA-1": 85,
        "SHA-256": 20,
        
        # Symmetric
        "DES": 95,
        "3DES": 75,
        "DESede": 75,
        "AES": 20,
        
        # Asymmetric & Certificates
        "RSA": 70,
        "EC": 40,
        "ECC": 40,
    }

    # Baseline score for unclassified dependencies
    _DEPENDENCY_BASELINE_SCORE = 30
    
    # Default fallback score for unknown algorithms
    _UNKNOWN_BASELINE_SCORE = 50

    @classmethod
    def score_assets(cls, assets: List[CryptoAsset]) -> List[CryptoAsset]:
        """
        Iterates over a list of CryptoAssets, calculates a risk score for each,
        assigns the appropriate Severity enum, and embeds the score in the metadata.
        Returns the modified list of assets.
        """
        for asset in assets:
            score = cls._calculate_score(asset)
            
            # Embed the numeric score for precise querying
            if asset.metadata is None:
                asset.metadata = {}
            asset.metadata["risk_score"] = score
            
            # Assign the severity bucket
            asset.severity = cls._determine_severity(score)
            
        return assets

    @classmethod
    def _calculate_score(cls, asset: CryptoAsset) -> int:
        """
        Determines the numeric risk score using deterministic rules.
        """
        if asset.asset_type == AssetType.DEPENDENCY:
            return cls._DEPENDENCY_BASELINE_SCORE
            
        if not asset.algorithm:
            return cls._UNKNOWN_BASELINE_SCORE
            
        # Upper case matching for robust lookup
        algo = asset.algorithm.upper()
        
        # Handle ECC curve variations (e.g., "ECC (secp256r1)") by extracting base name
        if algo.startswith("ECC") or algo.startswith("EC"):
            return cls._ALGORITHM_SCORES.get("EC", 40)
            
        return cls._ALGORITHM_SCORES.get(algo, cls._UNKNOWN_BASELINE_SCORE)

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
