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
        base_score = 0
        if asset.asset_type == AssetType.DEPENDENCY:
            base_score = policy.dependency_baseline_score
        elif not asset.algorithm:
            base_score = policy.unknown_baseline_score
        else:
            algo = asset.algorithm.upper()
            if algo.startswith("ECC") or algo.startswith("EC"):
                base_score = policy.algorithm_scores.get("EC", 40)
            else:
                base_score = policy.algorithm_scores.get(algo, policy.unknown_baseline_score)
                
        # Calculate CVE Penalty: Highest CVSS + 0.25 * sum(other_cvss)
        cve_penalty = 0.0
        cves = asset.metadata.get("cves", [])
        if cves:
            cvss_scores = [cve.get("cvss", 0.0) for cve in cves]
            if cvss_scores:
                cvss_scores.sort(reverse=True)
                highest_cvss = cvss_scores[0]
                other_cvss_sum = sum(cvss_scores[1:])
                total_cve_factor = highest_cvss + (0.25 * other_cvss_sum)
                cve_penalty = total_cve_factor * policy.cvss_weight_multiplier
                
        final_score = int(min(base_score + cve_penalty, 100))
        return final_score

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
