from typing import List
from app.services.graph_query_service import GraphQueryService
from app.services.migration_recommendation_service import MigrationRecommendationService
from app.models.migration_recommendation import MigrationRecommendation
from app.models.crypto_asset import CryptoAsset

class RecommendationWorkflowService:
    """
    Facade service orchestrating the generation of migration recommendations.
    Encapsulates database querying and DTO-to-Domain mapping to keep 
    presentation layers decoupled from business logic.
    """
    def __init__(self, query_service: GraphQueryService) -> None:
        self.query_service = query_service

    def generate_high_risk_recommendations(self) -> List[MigrationRecommendation]:
        """
        Retrieves high-risk assets from the graph database, hydrates them into 
        CryptoAsset domain models, and orchestrates the generation of recommendations.
        """
        try:
            raw_nodes = self.query_service.get_high_risk_assets()
            
            assets: List[CryptoAsset] = []
            for raw in raw_nodes:
                raw_dict = dict(raw)
                # Map Neo4j node type back to Pydantic Enum
                raw_dict["asset_type"] = raw_dict.get("node_type", "UNKNOWN")
                
                # Reconstruct metadata for the downstream service
                raw_dict["metadata"] = {
                    "risk_score": raw_dict.get("risk_score")
                }
                assets.append(CryptoAsset(**raw_dict))
                
            return MigrationRecommendationService.generate_recommendations(assets)
        finally:
            self.query_service.close()
