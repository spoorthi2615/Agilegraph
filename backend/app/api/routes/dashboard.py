from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from pathlib import Path

from app.config.settings import settings
from app.services.graph_query_service import GraphQueryService
from app.services.graph_rehydration_service import GraphRehydrationService
from app.services.recommendation_workflow_service import RecommendationWorkflowService
from app.services.pqc_readiness_service import PQCReadinessService
from app.services.migration_roadmap_service import MigrationRoadmapService
from app.services.security_report_service import SecurityReportService
from app.services.explainability_service import ExplainabilityService
from app.scanners.scanner_registry import get_default_registry
from app.graph.graph_builder import GraphBuilder

from app.models.project_analysis import ProjectAnalysisResult
from app.models.crypto_graph import CryptoGraph
from app.models.pqc_readiness import PQCReadinessAssessment
from app.models.migration_recommendation import MigrationRecommendation
from app.models.migration_roadmap import MigrationRoadmap
from app.models.explanation import Explanation
from app.models.security_report import SecurityReport

router = APIRouter()

# ---------------------------------------------------------
# Core Service Providers
# ---------------------------------------------------------

def get_query_service():
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        service.close()

def get_graph_rehydration_service(query_service: GraphQueryService = Depends(get_query_service)) -> GraphRehydrationService:
    return GraphRehydrationService(query_service=query_service)

def get_recommendation_workflow(query_service: GraphQueryService = Depends(get_query_service)) -> RecommendationWorkflowService:
    return RecommendationWorkflowService(query_service=query_service)

# ---------------------------------------------------------
# Orchestration Graph (Declarative Dependency Chain)
# ---------------------------------------------------------

def provide_analysis_result(project_id: str = "rehydrated-project") -> ProjectAnalysisResult:
    # A lightweight object to satisfy SecurityReportService's dependency without scanning
    return ProjectAnalysisResult(project_id=project_id, scanner_results=[])

def provide_crypto_graph(rehydration_service: GraphRehydrationService = Depends(get_graph_rehydration_service)) -> CryptoGraph:
    return rehydration_service.rehydrate_graph()

def provide_pqc_readiness(graph: CryptoGraph = Depends(provide_crypto_graph)) -> PQCReadinessAssessment:
    return PQCReadinessService.assess_readiness(graph)

def provide_recommendations(workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow)) -> List[MigrationRecommendation]:
    return workflow.generate_high_risk_recommendations()

def provide_roadmap(
    recommendations: List[MigrationRecommendation] = Depends(provide_recommendations),
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness)
) -> MigrationRoadmap:
    return MigrationRoadmapService.generate_roadmap(recommendations, readiness)

def provide_explanations(
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness),
    roadmap: MigrationRoadmap = Depends(provide_roadmap)
) -> List[Explanation]:
    return [
        ExplainabilityService.explain_readiness(readiness),
        ExplainabilityService.explain_roadmap(roadmap)
    ]

def provide_security_report(
    analysis_result: ProjectAnalysisResult = Depends(provide_analysis_result),
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness),
    roadmap: MigrationRoadmap = Depends(provide_roadmap),
    recommendations: List[MigrationRecommendation] = Depends(provide_recommendations),
    explanations: List[Explanation] = Depends(provide_explanations)
) -> SecurityReport:
    return SecurityReportService.generate_report(
        analysis_result=analysis_result,
        readiness=readiness,
        roadmap=roadmap,
        recommendations=recommendations,
        explanations=explanations
    )

# ---------------------------------------------------------
# Thin REST Controllers
# ---------------------------------------------------------

@router.get("/summary")
def get_summary(query_service: GraphQueryService = Depends(get_query_service)) -> Dict[str, int]:
    return query_service.get_summary_statistics()

@router.get("/report")
def get_report(report: SecurityReport = Depends(provide_security_report)) -> SecurityReport:
    return report

@router.get("/readiness")
def get_readiness(readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness)) -> PQCReadinessAssessment:
    return readiness

@router.get("/roadmap")
def get_roadmap(roadmap: MigrationRoadmap = Depends(provide_roadmap)) -> MigrationRoadmap:
    return roadmap

@router.get("/explanations")
def get_explanations(explanations: List[Explanation] = Depends(provide_explanations)) -> List[Explanation]:
    return explanations
