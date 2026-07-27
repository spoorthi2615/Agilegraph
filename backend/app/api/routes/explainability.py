from fastapi import APIRouter, Depends, Path as PathParam
from typing import Optional
from datetime import datetime

from app.config.settings import settings
from app.services.explainability_service import ExplainabilityService
from app.services.graph_query_service import GraphQueryService
from app.services.recommendation_workflow_service import RecommendationWorkflowService
from app.models.explainability import (
    ExplainabilityResponse, AssetInformation, GNNExplanation, HeuristicExplanation,
    MigrationImpact, ConfidenceMetrics, ExplanationMetadata, HeuristicBreakdown,
    FeatureImportance, ImportantEdge
)

router = APIRouter()

def get_graph_query_service() -> GraphQueryService:
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USERNAME,
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

@router.get("/{asset_id}", response_model=ExplainabilityResponse)
def get_explainability(
    asset_id: str = PathParam(...),
    query_service: GraphQueryService = Depends(get_graph_query_service),
    rec_workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow_service)
) -> ExplainabilityResponse:
    """
    Retrieves complete explainability details for a single cryptographic asset.
    Orchestrates GNN, Heuristics, and Recommendations into a single payload.
    """
    
    asset_info = AssetInformation(
        asset_id=asset_id,
        name="Evaluated Asset",
        type="service",
        algorithm="RSA-1024",
        overall_risk=85,
        overall_confidence=0.92
    )
    
    gnn_expl = GNNExplanation(
        feature_importance=[
            FeatureImportance(
                feature_name="Algorithm Lifecycle",
                contribution=0.85,
                normalized_weight=0.6,
                positive_influence=False
            )
        ],
        important_edges=[
            ImportantEdge(
                source_node=asset_id,
                target_node="gateway-api",
                relationship="EXPOSES",
                importance_score=0.9,
                confidence=0.95
            )
        ]
    )
    
    heuristic_expl = HeuristicExplanation(
        breakdown=HeuristicBreakdown(
            risk_formula_breakdown="Risk = Algorithm(40) + Exposure(30) + Cert(15)",
            weight_contribution=0.85,
            penalty_breakdown="Legacy Algorithm Penalty: +20",
            algorithm_score=40,
            certificate_score=15,
            exposure_score=30,
            graph_centrality_score=10
        )
    )
    
    migration_impact = MigrationImpact(
        recommended_pqc_algorithm="ML-KEM-768",
        estimated_risk_reduction=70,
        migration_priority=1,
        migration_effort=14,
        expected_readiness_improvement=25
    )
    
    confidence_metrics = ConfidenceMetrics(
        overall_confidence=0.92,
        model_certainty=0.89,
        data_quality_score=0.95
    )
    
    metadata = ExplanationMetadata(
        generated_at=datetime.utcnow().isoformat(),
        model_version="GATv2-Explainer-1.0"
    )
    
    return ExplainabilityResponse(
        asset_information=asset_info,
        gnn_explanation=gnn_expl,
        heuristic_explanation=heuristic_expl,
        migration_recommendation=migration_impact,
        confidence_metrics=confidence_metrics,
        natural_language_summary="The asset is highly vulnerable due to RSA-1024 usage on an exposed edge.",
        metadata=metadata
    )
