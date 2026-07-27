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

from app.models.dashboard import (
    DashboardSummary, KPISummary, DashboardGraph, DashboardNode, DashboardEdge, ReportRecord
)

router = APIRouter()

# ---------------------------------------------------------
# Core Service Providers
# ---------------------------------------------------------

def get_query_service():
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USERNAME,
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

@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    query_service: GraphQueryService = Depends(get_query_service),
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness)
) -> DashboardSummary:
    stats = query_service.get_summary_statistics()
    aggs = query_service.get_dashboard_aggregations()
    
    # Map severities
    severity_counts = {str(s["severity"]).upper(): s["count"] for s in aggs.get("severities", [])}
    critical_count = severity_counts.get("CRITICAL", 0)
    high_count = severity_counts.get("HIGH", 0)
    medium_count = severity_counts.get("MEDIUM", 0)
    low_count = severity_counts.get("LOW", 0)
    
    kpis = KPISummary(
        total_assets=stats.get("asset_count", 0),
        critical=critical_count,
        high=high_count,
        medium=medium_count,
        low=low_count,
        migration_progress=0,  # Could be derived from migrated assets if tracked
        pqc_readiness=readiness.overall_readiness_score if readiness else 0,
        last_scan="Recent"
    )
    
    # Map Risk Distribution
    risk_dist = [
        RiskDistribution(name="Critical", value=critical_count, color="#ef4444"),
        RiskDistribution(name="High", value=high_count, color="#f97316"),
        RiskDistribution(name="Medium", value=medium_count, color="#eab308"),
        RiskDistribution(name="Low", value=low_count, color="#22c55e")
    ]
    
    # Map Algorithm Usage
    algo_usage = [
        AlgorithmUsage(algorithm=str(a["algorithm"]), count=a["count"])
        for a in aggs.get("algorithms", [])
    ]
    
    # Map Alerts
    alerts = [
        CriticalAlert(
            id=str(alert["id"]), 
            title=str(alert["title"]), 
            reason=str(alert["reason"]), 
            score=alert["score"]
        )
        for alert in aggs.get("alerts", [])
    ]
    
    return DashboardSummary(
        kpis=kpis,
        risk_distribution=risk_dist,
        algorithm_usage=algo_usage,
        department_usage=[],  # Keep empty for now as departments aren't in the AST
        migration_trend=[MigrationTrend(month="Current", migrated=0, planned=critical_count + high_count)],
        recent_scans=[],
        activity=[],
        critical_alerts=alerts
    )

@router.get("/graph", response_model=DashboardGraph)
def get_graph(graph: CryptoGraph = Depends(provide_crypto_graph)) -> DashboardGraph:
    nodes = []
    if graph and hasattr(graph, 'nodes'):
        for node in graph.nodes:
            # We must map backend CryptoNode to frontend DashboardNode
            # Risk level fallback to "medium", type fallback to "service" if undefined
            nodes.append(DashboardNode(
                id=str(node.node_id),
                label=str(node.name) if hasattr(node, 'name') else str(node.node_id),
                type="service", 
                risk="medium",
                x=0.0, 
                y=0.0
            ))
            
    edges = []
    if graph and hasattr(graph, 'edges'):
        for edge in graph.edges:
            edges.append(DashboardEdge(
                source=str(edge.source_id),
                target=str(edge.target_id)
            ))
            
    return DashboardGraph(nodes=nodes, edges=edges)

@router.get("/reports", response_model=List[ReportRecord])
def get_reports(report: SecurityReport = Depends(provide_security_report)) -> List[ReportRecord]:
    if not report:
        return []
        
    return [
        ReportRecord(
            id=str(report.report_id),
            title="Generated Security Report",
            type="Security",
            created_at=report.generated_at.isoformat() if hasattr(report, 'generated_at') else "",
            size="0 KB",
            author="AgileGraph"
        )
    ]

@router.get("/explanations", response_model=List[Explanation])
def get_explanations(explanations: List[Explanation] = Depends(provide_explanations)) -> List[Explanation]:
    return explanations if explanations else []
