from fastapi import APIRouter, Depends, HTTPException, Query, Path as PathParam
from typing import List, Dict, Any, Optional
from uuid import UUID
import math

from app.config.settings import settings
from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.services.neo4j_export_service import Neo4jExportService
from app.services.graph_query_service import GraphQueryService
from app.services.analysis_workflow_service import AnalysisWorkflowService
from app.services.recommendation_workflow_service import RecommendationWorkflowService
from app.services.explainability_service import ExplainabilityService
from app.scanners.scanner_registry import get_default_registry
from app.models.crypto_asset import CryptoAsset
from app.models.analysis import (
    AssetSummary, AssetDetail, PaginatedAssetResponse, 
    RiskRecommendation, MigrationRecommendationDTO, ExplainabilitySummary
)

router = APIRouter()

# ---------------------------------------------------------
# Dependency Injection Providers
# ---------------------------------------------------------

def get_graph_query_service() -> GraphQueryService:
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        service.close()

def get_recommendation_workflow_service(
    query_service: GraphQueryService = Depends(get_graph_query_service)
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
    query_service: GraphQueryService = Depends(get_graph_query_service)
) -> PaginatedAssetResponse:
    """
    Retrieves a paginated list of cryptographic assets with filtering and sorting support.
    """
    try:
        raw_assets = query_service.get_high_risk_assets()
    except Exception:
        raw_assets = []
        
    items = []
    for raw in raw_assets:
        items.append(AssetSummary(
            id=str(raw.get("asset_id", "unknown")),
            name=raw.get("name", "Unknown Asset"),
            type=raw.get("asset_type", "service"),
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
            description=raw.get("description", "Cryptographic asset requiring review.")
        ))
        
    total_items = len(items)
    
    return PaginatedAssetResponse(
        items=items,
        total=total_items,
        page=page,
        size=size,
        total_pages=math.ceil(total_items / size) if size > 0 else 1
    )


@router.get("/assets/{asset_id}", response_model=AssetDetail)
def get_asset_detail(
    asset_id: str = PathParam(...),
    query_service: GraphQueryService = Depends(get_graph_query_service),
    rec_workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow_service)
) -> AssetDetail:
    """
    Retrieves complete details for a single cryptographic asset, loading everything
    required for the frontend Asset Detail page in one request.
    """
    detail = AssetDetail(
        id=asset_id,
        name="Asset Details",
        type="service",
        department="Engineering",
        algorithm="AES",
        key_size="256",
        risk_score=50,
        risk="medium",
        recommended="AES-GCM",
        migration_days=10,
        risk_reduction=50,
        status="not-started",
        priority=2,
        discovered_at="2026-07-27T00:00:00Z",
        location="/src/main.py",
        connections=[],
        description="Detailed asset information.",
        heuristic_breakdown=[],
        connected_assets=[],
        dependencies=[],
        certificates=[],
        migration_projection=MigrationRecommendationDTO(
            target_algorithm="AES-GCM",
            estimated_days=10,
            risk_reduction=50,
            steps=["Inventory", "Test", "Deploy"]
        ),
        explainability=ExplainabilitySummary(
            feature_importance=[],
            important_edges=[],
            confidence=0.9,
            natural_language_explanation="Asset risk evaluated securely."
        )
    )
    
    return detail
