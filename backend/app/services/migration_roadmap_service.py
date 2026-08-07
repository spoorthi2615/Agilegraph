from typing import List

from app.models.migration_recommendation import MigrationRecommendation, Priority
from app.models.migration_roadmap import MigrationRoadmap
from app.models.pqc_readiness import PQCReadinessAssessment


class MigrationRoadmapService:
    """
    Service responsible for aggregating tactical migration recommendations and
    macro-level PQC readiness assessments into a strategic, phased migration roadmap.
    """

    @classmethod
    def generate_roadmap(
        cls,
        recommendations: List[MigrationRecommendation],
        readiness: PQCReadinessAssessment,
    ) -> MigrationRoadmap:
        """
        Groups migration recommendations into execution phases and generates an
        executive summary based on the organization's PQC readiness state.
        """
        immediate_actions = 0
        high_priority = 0
        medium_priority = 0
        low_priority = 0

        # Aggregate recommendations by strategic phase
        for rec in recommendations:
            if rec.priority == Priority.IMMEDIATE:
                immediate_actions += 1
            elif rec.priority == Priority.HIGH:
                high_priority += 1
            elif rec.priority == Priority.MEDIUM:
                medium_priority += 1
            elif rec.priority == Priority.LOW:
                low_priority += 1

        # Calculate active phases. If a phase has 0 actions, it doesn't require execution time.
        active_phases = sum(
            1
            for phase in [
                immediate_actions,
                high_priority,
                medium_priority,
                low_priority,
            ]
            if phase > 0
        )

        # Generate the strategic executive summary
        summary = (
            f"The organization is currently classified as {readiness.readiness_level.value} "
            f"with a Post-Quantum Cryptography (PQC) readiness score of {readiness.overall_score:.1f}%. "
            f"There are {readiness.migration_candidates} cryptographic assets identified as migration candidates. "
            f"To achieve compliance, the migration strategy has been organized into {active_phases} estimated execution phases."
        )

        return MigrationRoadmap(
            readiness_score=readiness.overall_score,
            readiness_level=readiness.readiness_level.value,
            total_recommendations=len(recommendations),
            immediate_actions=immediate_actions,
            high_priority_actions=high_priority,
            medium_priority_actions=medium_priority,
            low_priority_actions=low_priority,
            estimated_phases=active_phases,
            executive_summary=summary,
        )
