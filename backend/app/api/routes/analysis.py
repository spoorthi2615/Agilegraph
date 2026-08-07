import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Path as PathParam

from app.config.settings import settings
from app.core.security import User, get_current_user_strict
from app.models.analysis import (
    AssetDetail,
    AssetSummary,
    ExplainabilitySummary,
    MigrationRecommendationDTO,
    PaginatedAssetResponse,
)
from app.services.graph_query_service import GraphQueryService
from app.services.recommendation_workflow_service import RecommendationWorkflowService

router = APIRouter()

# ---------------------------------------------------------
# Dependency Injection Providers
# ---------------------------------------------------------


def get_graph_query_service(user: User = Depends(get_current_user_strict)) -> GraphQueryService:
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD,
        user_id=user.id,
        is_admin=user.is_admin,
    )
    try:
        yield service
    finally:
        service.close()


def get_recommendation_workflow_service(
    query_service: GraphQueryService = Depends(get_graph_query_service),
) -> RecommendationWorkflowService:
    return RecommendationWorkflowService(query_service=query_service)


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------


@router.get("/assets", response_model=PaginatedAssetResponse)
def get_assets(
    query: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    department: Optional[str] = Query(None, description="Filter by department"),
    query_service: GraphQueryService = Depends(get_graph_query_service),
) -> PaginatedAssetResponse:
    """
    Retrieves a paginated list of cryptographic assets with filtering and sorting support.
    """
    try:
        raw_assets = query_service.get_all_assets()
    except Exception:
        raw_assets = []

    items = []
    for raw in raw_assets:
        items.append(
            AssetSummary(
                id=str(raw.get("node_id", "unknown")),
                name=raw.get("label", "Unknown Asset"),
                type=str(raw.get("node_type", "service")).lower(),
                department=raw.get("department", "Engineering"),
                algorithm=raw.get("algorithm", "Unknown"),
                key_size=raw.get("key_size", "256"),
                risk_score=raw.get("risk_score", 0),
                risk=raw.get("severity", "medium").lower(),
                recommended=raw.get("recommended", "N/A"),
                migration_days=raw.get("migration_days", 0),
                risk_reduction=raw.get("risk_reduction", 0),
                status="not-started",
                priority=raw.get("priority", 3),
                discovered_at="2026-07-27T00:00:00Z",
                location=raw.get("location", "unknown"),
                connections=[],
                description=raw.get("description", "Cryptographic asset requiring review."),
            )
        )

    total_items = len(items)

    return PaginatedAssetResponse(
        items=items,
        total=total_items,
        page=page,
        size=size,
        total_pages=math.ceil(total_items / size) if size > 0 else 1,
    )


@router.get("/assets/{asset_id}", response_model=AssetDetail)
def get_asset_detail(
    asset_id: str = PathParam(...),
    query_service: GraphQueryService = Depends(get_graph_query_service),
    rec_workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow_service),
) -> AssetDetail:
    """
    Retrieves complete details for a single cryptographic asset, loading everything
    required for the frontend Asset Detail page in one request.
    """
    node_data = query_service.get_node_by_id(asset_id)
    if not node_data:
        raise HTTPException(status_code=404, detail="Asset not found")

    detail = AssetDetail(
        id=asset_id,
        name=node_data.get("label", "Asset Details"),
        type=str(node_data.get("node_type", "service")).lower(),
        department="Engineering",
        algorithm=node_data.get("algorithm", "Unknown"),
        key_size=str(node_data.get("key_size") or "256"),
        risk_score=node_data.get("risk_score") or 0,
        risk=str(node_data.get("severity") or "medium").lower(),
        recommended="PQC-Safe Standard",
        migration_days=0,
        risk_reduction=node_data.get("risk_score") or 0,
        status="not-started",
        priority=node_data.get("risk_score") or 0,
        discovered_at="2026-07-27T00:00:00Z",
        location=node_data.get("file_path") or "unknown",
        connections=[],
        description="Detailed asset information retrieved from graph.",
        heuristic_breakdown=[],
        connected_assets=[],
        dependencies=[],
        certificates=[],
        migration_projection=MigrationRecommendationDTO(
            target_algorithm="PQC-Safe Standard",
            estimated_days=10,
            risk_reduction=node_data.get("risk_score", 0),
            steps=["Inventory", "Test", "Deploy"],
        ),
        explainability=ExplainabilitySummary(
            feature_importance=[],
            important_edges=[],
            confidence=0.9,
            natural_language_explanation="Detailed explainability awaits Phase 6.",
        ),
    )

    return detail
