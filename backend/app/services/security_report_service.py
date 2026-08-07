from typing import List

from app.models.explanation import Explanation
from app.models.migration_recommendation import MigrationRecommendation
from app.models.migration_roadmap import MigrationRoadmap
from app.models.pqc_readiness import PQCReadinessAssessment
from app.models.project_analysis import ProjectAnalysisResult
from app.models.security_report import SecurityReport


class SecurityReportService:
    """
    Service responsible for aggregating disparate analytical outputs, assessments,
    and explanations into a singular, comprehensive executive security report.
    """

    @classmethod
    def generate_report(
        cls,
        analysis_result: ProjectAnalysisResult,
        readiness: PQCReadinessAssessment,
        roadmap: MigrationRoadmap,
        recommendations: List[MigrationRecommendation],
        explanations: List[Explanation],
        total_cves: int = 0,
        mosca_status: str = "Unknown",
    ) -> SecurityReport:
        """
        Consolidates the entire analytical output of the AgileGraph pipeline into
        a single, definitive SecurityReport artifact.
        """
        total_assets = readiness.total_crypto_assets

        # High-risk assets are objectively defined as possessing a risk score of 75 or higher
        total_high_risk = sum(1 for rec in recommendations if rec.risk_score >= 75)

        # Generate a deterministic, human-readable executive summary
        executive_summary = (
            f"AgileGraph successfully completed a cryptographic analysis sweep for project '{analysis_result.project_id}'. "
            f"A total of {total_assets} cryptographic assets were discovered in the codebase, of which {total_high_risk} "
            f"are classified as high-risk (Severity: HIGH or CRITICAL). The project achieved a Post-Quantum "
            f"Cryptography (PQC) readiness score of {readiness.overall_score:.1f}% ({readiness.readiness_level.value}). "
            f"To achieve full security compliance, a {roadmap.estimated_phases}-phase migration roadmap has been generated, "
            f"comprising {len(recommendations)} actionable recommendations."
        )

        return SecurityReport(
            project_id=analysis_result.project_id,
            total_assets=total_assets,
            total_high_risk_assets=total_high_risk,
            pqc_readiness_score=readiness.overall_score,
            pqc_readiness_level=readiness.readiness_level,
            total_recommendations=len(recommendations),
            roadmap_summary=roadmap.executive_summary,
            executive_summary=executive_summary,
            recommendations=recommendations,
            explanations=explanations,
            total_cves=total_cves,
            mosca_status=mosca_status,
        )
