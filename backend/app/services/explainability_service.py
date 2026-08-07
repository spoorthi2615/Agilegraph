from app.models.crypto_asset import CryptoAsset
from app.models.explanation import Explanation, ExplanationType
from app.models.migration_recommendation import MigrationRecommendation
from app.models.migration_roadmap import MigrationRoadmap
from app.models.pqc_readiness import PQCReadinessAssessment


class ExplainabilityService:
    """
    Service responsible for generating deterministic, template-based, auditable
    explanations for cryptographic risks, recommendations, and strategic roadmaps.
    """

    @classmethod
    def explain_risk(cls, asset: CryptoAsset) -> Explanation:
        """
        Generates a deterministic explanation for why a specific asset received its risk score.
        """
        score = asset.metadata.get("risk_score", "Unknown")
        severity = asset.severity.value if asset.severity else "Unknown"
        algo = asset.algorithm or "Unknown"

        explanation_text = (
            f"The cryptographic algorithm '{algo}' was evaluated and assigned a risk score "
            f"of {score} ({severity} severity) based on deterministic mapping rules from NIST guidelines."
        )

        evidence = [
            f"Algorithm detected: {algo}",
            f"Risk Score assigned: {score}",
            f"Severity assigned: {severity}",
        ]

        if asset.metadata.get("contextual_risk") is not None:
            ctx_risk = asset.metadata["contextual_risk"]
            evidence.append(f"Contextual risk (maximum connected structural risk) is {ctx_risk}")

        return Explanation(
            asset_id=asset.asset_id,
            explanation_type=ExplanationType.RISK,
            title=f"Risk Assessment for {algo}",
            explanation=explanation_text,
            supporting_evidence=evidence,
        )

    @classmethod
    def explain_migration(cls, rec: MigrationRecommendation) -> Explanation:
        """
        Generates a deterministic explanation detailing the rationale behind a specific migration path.
        """
        explanation_text = (
            f"A migration to {rec.recommended_algorithm} is recommended for the asset currently utilizing {rec.algorithm}. "
            f"This actionable recommendation is strictly based on its risk profile and standard cryptographic deprecation schedules."
        )

        evidence = [
            f"Original vulnerable algorithm: {rec.algorithm}",
            f"Recommended secure algorithm: {rec.recommended_algorithm}",
            f"Rationale provided by system: {rec.rationale}",
            f"Action Priority Level: {rec.priority.value}",
        ]

        return Explanation(
            asset_id=rec.asset_id,
            explanation_type=ExplanationType.MIGRATION,
            title=f"Migration Path Formulation: {rec.recommended_algorithm}",
            explanation=explanation_text,
            supporting_evidence=evidence,
        )

    @classmethod
    def explain_readiness(cls, readiness: PQCReadinessAssessment) -> Explanation:
        """
        Generates a deterministic explanation breaking down the mathematics of the PQC readiness score.
        """
        explanation_text = (
            f"The project has been assessed at a PQC Readiness score of {readiness.overall_score}% "
            f"({readiness.readiness_level.value}). This score is calculated mathematically by isolating "
            f"the ratio of definitively quantum-safe assets to total cryptographic assets."
        )

        evidence = [
            f"Total cryptographic assets discovered: {readiness.total_crypto_assets}",
            f"Assets confirmed as PQC-ready (e.g. AES, SHA-256): {readiness.pqc_ready_assets}",
            f"Assets classified as classical/vulnerable: {readiness.classical_assets}",
            "Score Formula: (pqc_ready_assets / total_crypto_assets) * 100",
        ]

        return Explanation(
            asset_id=None,
            explanation_type=ExplanationType.READINESS,
            title="PQC Readiness Mathematical Breakdown",
            explanation=explanation_text,
            supporting_evidence=evidence,
        )

    @classmethod
    def explain_roadmap(cls, roadmap: MigrationRoadmap) -> Explanation:
        """
        Generates a deterministic explanation for how the phased migration strategy was structured.
        """
        explanation_text = (
            f"The migration strategy is divided into {roadmap.estimated_phases} dynamic execution phases. "
            "These phases are calculated by grouping individual migration recommendations based entirely "
            "on their deterministic risk priority levels, ensuring immediate threats are resolved in Phase 1."
        )

        evidence = [
            f"Phase 1 (Immediate Priority) Actions required: {roadmap.immediate_actions}",
            f"Phase 2 (High Priority) Actions required: {roadmap.high_priority_actions}",
            f"Phase 3 (Medium Priority) Actions required: {roadmap.medium_priority_actions}",
            f"Phase 4 (Low Priority) Actions required: {roadmap.low_priority_actions}",
            f"Total Recommendations processed into phases: {roadmap.total_recommendations}",
        ]

        return Explanation(
            asset_id=None,
            explanation_type=ExplanationType.ROADMAP,
            title="Phased Migration Strategy Formulation",
            explanation=explanation_text,
            supporting_evidence=evidence,
        )
