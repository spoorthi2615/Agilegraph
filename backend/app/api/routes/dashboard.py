from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.config.settings import settings
from app.core.security import User, get_current_user_strict
from app.models.crypto_graph import CryptoGraph
from app.models.dashboard import (
    ActivityItem,
    AlgorithmUsage,
    CriticalAlert,
    DashboardEdge,
    DashboardGraph,
    DashboardNode,
    DashboardSummary,
    DepartmentUsage,
    KPISummary,
    MigrationTrend,
    ReportRecord,
    RiskDistribution,
    ScanRecord,
)
from app.models.explanation import Explanation
from app.models.migration_recommendation import MigrationRecommendation
from app.models.migration_roadmap import MigrationRoadmap
from app.models.pqc_readiness import PQCReadinessAssessment
from app.models.project_analysis import ProjectAnalysisResult
from app.models.security_report import SecurityReport
from app.services.explainability_service import ExplainabilityService
from app.services.graph_query_service import GraphQueryService
from app.services.graph_rehydration_service import GraphRehydrationService
from app.services.migration_roadmap_service import MigrationRoadmapService
from app.services.pqc_readiness_service import PQCReadinessService
from app.services.recommendation_workflow_service import RecommendationWorkflowService
from app.services.security_report_service import SecurityReportService

router = APIRouter()

# ---------------------------------------------------------
# Core Service Providers
# ---------------------------------------------------------


def get_query_service(user: User = Depends(get_current_user_strict)):
    if not settings.NEO4J_URI:
        yield None
        return

    try:
        service = GraphQueryService(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        yield service
    except Exception:
        yield None  # Neo4j unavailable — endpoints handle None gracefully
    finally:
        try:
            if "service" in locals() and service is not None:
                service.close()
        except Exception:
            pass


def get_graph_rehydration_service(
    query_service: GraphQueryService = Depends(get_query_service),
) -> GraphRehydrationService:
    return GraphRehydrationService(query_service=query_service)


def get_recommendation_workflow(
    query_service: GraphQueryService = Depends(get_query_service),
) -> RecommendationWorkflowService:
    return RecommendationWorkflowService(query_service=query_service)


# ---------------------------------------------------------
# Orchestration Graph (Declarative Dependency Chain)
# ---------------------------------------------------------


def provide_analysis_result(
    project_id: str = "rehydrated-project",
) -> ProjectAnalysisResult:
    # A lightweight object to satisfy SecurityReportService's dependency without scanning
    return ProjectAnalysisResult(project_id=project_id, scanner_results=[])


def provide_crypto_graph(
    rehydration_service: GraphRehydrationService = Depends(get_graph_rehydration_service),
) -> CryptoGraph:
    return rehydration_service.rehydrate_graph()


def provide_pqc_readiness(
    graph: CryptoGraph = Depends(provide_crypto_graph),
) -> PQCReadinessAssessment:
    return PQCReadinessService.assess_readiness(graph)


def provide_recommendations(
    workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow),
) -> List[MigrationRecommendation]:
    return workflow.generate_high_risk_recommendations()


def provide_roadmap(
    recommendations: List[MigrationRecommendation] = Depends(provide_recommendations),
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness),
) -> MigrationRoadmap:
    return MigrationRoadmapService.generate_roadmap(recommendations, readiness)


def provide_explanations(
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness),
    roadmap: MigrationRoadmap = Depends(provide_roadmap),
) -> List[Explanation]:
    return [
        ExplainabilityService.explain_readiness(readiness),
        ExplainabilityService.explain_roadmap(roadmap),
    ]


def provide_security_report(
    analysis_result: ProjectAnalysisResult = Depends(provide_analysis_result),
    readiness: PQCReadinessAssessment = Depends(provide_pqc_readiness),
    roadmap: MigrationRoadmap = Depends(provide_roadmap),
    recommendations: List[MigrationRecommendation] = Depends(provide_recommendations),
    explanations: List[Explanation] = Depends(provide_explanations),
    graph: CryptoGraph = Depends(provide_crypto_graph),
) -> SecurityReport:
    total_cves = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for node in graph.nodes.values():
        cves = node.metadata.get("cves", [])
        if cves:
            total_cves += len(cves)

        severity = str(node.severity).upper() if node.severity else "LOW"
        if severity == "CRITICAL":
            critical_count += 1
        elif severity == "HIGH":
            high_count += 1
        elif severity == "MEDIUM":
            medium_count += 1
        else:
            low_count += 1

    y = round(
        (critical_count * 0.1) + (high_count * 0.05) + (medium_count * 0.02) + (low_count * 0.01),
        1,
    )
    if critical_count > 0:
        x = 10.0
    elif high_count > 0:
        x = 7.0
    elif medium_count > 0:
        x = 3.0
    else:
        x = 1.0
    z = 8.0

    from app.services.mosca_service import MoscaService

    mosca_result = MoscaService.calculate_index(x, y, z)

    return SecurityReportService.generate_report(
        analysis_result=analysis_result,
        readiness=readiness,
        roadmap=roadmap,
        recommendations=recommendations,
        explanations=explanations,
        total_cves=total_cves,
        mosca_status=mosca_result["status"],
    )


# ---------------------------------------------------------
# Thin REST Controllers
# ---------------------------------------------------------


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    query_service: GraphQueryService = Depends(get_query_service),
) -> DashboardSummary:
    try:
        if query_service is None:
            raise RuntimeError("Neo4j unavailable")
        stats = query_service.get_summary_statistics()
        aggs = query_service.get_dashboard_aggregations()
    except Exception:
        # Return clean empty dashboard when Neo4j is unreachable
        return DashboardSummary(
            kpis=KPISummary(
                total_assets=0,
                critical=0,
                high=0,
                medium=0,
                low=0,
                migration_progress=0,
                pqc_readiness=0,
                last_scan="No scans yet",
                active_migrations=0,
            ),
            risk_distribution=[
                RiskDistribution(name="Critical", value=0, color="#ef4444"),
                RiskDistribution(name="High", value=0, color="#f97316"),
                RiskDistribution(name="Medium", value=0, color="#eab308"),
                RiskDistribution(name="Low", value=0, color="#22c55e"),
            ],
            algorithm_usage=[],
            department_usage=[],
            migration_trend=[MigrationTrend(month="Current", migrated=0, planned=0)],
            recent_scans=[],
            activity=[],
            critical_alerts=[],
        )

    # Map severities
    severity_counts = {str(s["severity"]).upper(): s["count"] for s in aggs.get("severities", [])}
    critical_count = severity_counts.get("CRITICAL", 0)
    high_count = severity_counts.get("HIGH", 0)
    medium_count = severity_counts.get("MEDIUM", 0)
    low_count = severity_counts.get("LOW", 0)

    total_vulnerable = critical_count + high_count + medium_count + low_count
    y = round(
        (critical_count * 0.1) + (high_count * 0.05) + (medium_count * 0.02) + (low_count * 0.01),
        1,
    )
    if total_vulnerable > 0 and y < 0.5:
        y = 0.5
    if critical_count > 0:
        x = 10.0
    elif high_count > 0:
        x = 7.0
    elif medium_count > 0:
        x = 3.0
    else:
        x = 1.0

    z = 8.0
    raw_readiness = max(0, min(100, ((z - max(x + y, 0.1)) / z) * 100 + 40))
    pqc_readiness_score = int(round(raw_readiness))

    kpis = KPISummary(
        total_assets=stats.get("asset_count", 0),
        critical=critical_count,
        high=high_count,
        medium=medium_count,
        low=low_count,
        migration_progress=0 if stats.get("asset_count", 0) == 0 else 12, # Still placeholder for now but 0 when no data
        pqc_readiness=pqc_readiness_score,
        last_scan="No scans yet" if stats.get("asset_count", 0) == 0 else "2h ago",
        active_migrations=0 if stats.get("asset_count", 0) == 0 else 9,
    )

    risk_dist = [
        RiskDistribution(name="Critical", value=critical_count, color="#ef4444"),
        RiskDistribution(name="High", value=high_count, color="#f97316"),
        RiskDistribution(name="Medium", value=medium_count, color="#eab308"),
        RiskDistribution(name="Low", value=low_count, color="#22c55e"),
    ]

    algo_usage = [
        AlgorithmUsage(algorithm=str(a["algorithm"]), count=a["count"])
        for a in aggs.get("algorithms", [])
    ]

    alerts = [
        CriticalAlert(
            id=str(alert["id"]),
            title=str(alert["title"]),
            reason=str(alert["reason"]),
            score=alert["score"],
        )
        for alert in aggs.get("alerts", [])
    ]

    scans = []
    if stats.get("asset_count", 0) > 0:
        # Check if the user is an admin or not for dashboard view
        # Note: In real life this would query 'recent scans' from Neo4j, but here we just mock the display
        scans.append(
            ScanRecord(
                id="SCAN-94A8B",
                name="core-banking-monorepo",
                source="GitHub",
                started_at="2 hours ago",
                duration="4m 12s",
                assets=stats.get("asset_count", 0),
                critical_findings=critical_count,
                status="Completed",
            )
        )

    dept_usage = [
        DepartmentUsage(
            department="Engineering",
            assets=stats.get("asset_count", 0),
            critical=critical_count,
        )
    ]

    activities = [
        ActivityItem(
            id="ACT-1",
            actor="Scanner Bot",
            action="completed baseline scan on",
            target="Acme Bank Production",
            time="Just now",
            kind="scan",
        )
    ]

    return DashboardSummary(
        kpis=kpis,
        risk_distribution=risk_dist,
        algorithm_usage=algo_usage,
        department_usage=dept_usage,
        migration_trend=[
            MigrationTrend(month="Current", migrated=0, planned=critical_count + high_count)
        ],
        recent_scans=scans,
        activity=activities,
        critical_alerts=alerts,
    )


class MoscaResponse(BaseModel):
    x: float
    y: float
    z: float
    surplus: float
    readiness_score: int
    has_data: bool


@router.get("/mosca", response_model=MoscaResponse)
def get_mosca_readiness(
    z: float = Query(8.0, description="Quantum horizon in years"),
    query_service: GraphQueryService = Depends(get_query_service),
) -> MoscaResponse:
    try:
        if query_service is None:
            raise RuntimeError("Neo4j unavailable")

        # Get aggregations to compute real X and Y
        aggs = query_service.get_dashboard_aggregations()
        severity_counts = {
            str(s["severity"]).upper(): s["count"] for s in aggs.get("severities", [])
        }

        critical_count = severity_counts.get("CRITICAL", 0)
        high_count = severity_counts.get("HIGH", 0)
        medium_count = severity_counts.get("MEDIUM", 0)
        low_count = severity_counts.get("LOW", 0)

        total_vulnerable = critical_count + high_count + medium_count + low_count

        # Y: Estimated migration duration based on volume and complexity
        # Assume: 0.1 years per critical, 0.05 per high, 0.02 per medium, 0.01 per low
        y = round(
            (critical_count * 0.1)
            + (high_count * 0.05)
            + (medium_count * 0.02)
            + (low_count * 0.01),
            1,
        )
        # Ensure minimum 0.5 years if there are any vulnerable assets
        if total_vulnerable > 0 and y < 0.5:
            y = 0.5

        # X: Required data confidentiality lifetime based on highest criticality
        # A project with critical assets requires longer secrecy
        if critical_count > 0:
            x = 10.0
        elif high_count > 0:
            x = 7.0
        elif medium_count > 0:
            x = 3.0
        else:
            x = 1.0

        surplus = round(z - (x + y), 1)

        # Calculate readiness score (0-100) based on the surplus
        if z <= 0.0:
            raw = 0
        else:
            raw = max(0, min(100, ((z - max(x + y, 0.1)) / z) * 100 + 40))
        readiness_score = int(round(raw))

        stats = query_service.get_summary_statistics()
        has_data = stats.get("asset_count", 0) > 0

        return MoscaResponse(
            x=x,
            y=y,
            z=z,
            surplus=surplus,
            readiness_score=readiness_score,
            has_data=has_data,
        )
    except Exception:
        # Fallback for when Neo4j is unavailable
        return MoscaResponse(
            x=1.0,
            y=0.5,
            z=z,
            surplus=round(z - 1.5, 1),
            readiness_score=80,
            has_data=False,
        )


@router.get("/graph", response_model=DashboardGraph)
def get_graph(graph: CryptoGraph = Depends(provide_crypto_graph)) -> DashboardGraph:
    nodes = []
    if graph and hasattr(graph, "nodes"):
        for node in graph.nodes.values():
            # We must map backend CryptoNode to frontend DashboardNode
            # Risk level fallback to "medium", type fallback to "service" if undefined
            nodes.append(
                DashboardNode(
                    id=str(node.node_id),
                    label=(str(node.label) if hasattr(node, "label") else str(node.node_id)),
                    type="service",
                    risk="medium",
                    x=0.0,
                    y=0.0,
                )
            )

    edges = []
    if graph and hasattr(graph, "edges"):
        for edge in graph.edges:
            edges.append(DashboardEdge(source=str(edge.source_node), target=str(edge.target_node)))

    return DashboardGraph(nodes=nodes, edges=edges)


@router.get("/reports", response_model=List[ReportRecord])
def get_reports(
    report: SecurityReport = Depends(provide_security_report),
) -> List[ReportRecord]:
    from app.api.routes.report import GENERATED_REPORTS

    return GENERATED_REPORTS


@router.get("/explanations", response_model=List[Explanation])
def get_explanations(
    explanations: List[Explanation] = Depends(provide_explanations),
) -> List[Explanation]:
    return explanations if explanations else []
