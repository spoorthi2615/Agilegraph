from pathlib import Path
from typing import Dict, Any

from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.graph.graph_builder import GraphBuilder
from app.services.neo4j_export_service import Neo4jExportService
from app.models.crypto_asset import CryptoAsset

class AnalysisWorkflowService:
    """
    Facade service orchestrating the entire static analysis pipeline.
    Encapsulates all domain transformations and state mutations so that
    presentation layers (like REST routers) remain strictly decoupled.
    """
    def __init__(
        self,
        analysis_service: ProjectAnalysisService,
        export_service: Neo4jExportService
    ) -> None:
        self.analysis_service = analysis_service
        self.export_service = export_service

    def execute_pipeline(self, project_id: str, project_path: Path) -> Dict[str, Any]:
        """
        Sequentially executes the scan, score, graph build, and export workflow.
        Returns a simplified statistics summary object.
        """
        try:
            # Step 1: Execute static analysis scanners
            analysis_result = self.analysis_service.analyze_project(project_id, project_path)
            
            # Step 2: Apply risk scoring rules via internal hydration/dehydration
            for scanner_result in analysis_result.scanner_results:
                assets = [CryptoAsset(**finding) for finding in scanner_result.findings]
                scored_assets = RiskScoringService.score_assets(assets)
                scanner_result.findings = [asset.model_dump(mode="json") for asset in scored_assets]
                
            # Step 3: Transform into Graph Domain Model
            graph = GraphBuilder.build_graph(analysis_result)
            
            # Step 4: Export to physical Neo4j cluster
            self.export_service.export_graph(graph)
            
            # Return standardized metrics
            return {
                "status": "success",
                "total_findings": analysis_result.total_findings,
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges)
            }
            
        finally:
            self.export_service.close()
