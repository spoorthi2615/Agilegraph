from typing import Dict, Any
import logging
from pydantic import ValidationError
from app.models.project_analysis import ProjectAnalysisResult
from app.models.crypto_graph import CryptoGraph
from app.models.graph_node import GraphNode
from app.models.crypto_asset import CryptoAsset

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Transforms a ProjectAnalysisResult into an in-memory CryptoGraph.
    Responsible strictly for structural mapping, devoid of scanning or traversal logic.
    """

    @staticmethod
    def build_graph(analysis_result: ProjectAnalysisResult) -> CryptoGraph:
        """
        Converts the results of the orchestration pipeline into a graph.
        Currently, this intentionally generates only nodes, deferring relationship creation.
        
        Args:
            analysis_result (ProjectAnalysisResult): The aggregated output from all scanners.
            
        Returns:
            CryptoGraph: The in-memory graph representation.
        """
        graph = CryptoGraph()

        # Step 2: Iterate through every ScannerResult
        for scanner_result in analysis_result.scanner_results:
            
            # Step 3: Iterate through every finding contained inside each ScannerResult
            for finding_dict in scanner_result.findings:
                # Limitation Note: findings are currently stored as dictionaries due to 
                # ScannerResult flexibility requirements. We rehydrate them to CryptoAssets.
                try:
                    asset = CryptoAsset(**finding_dict)
                except ValidationError as e:
                    logger.error(f"Skipping malformed finding from scanner '{scanner_result.scanner_name}': {str(e)}")
                    continue
                
                # Step 4: Convert every CryptoAsset into one GraphNode
                
                # Label must use ONLY the algorithm name
                label = asset.algorithm if asset.algorithm else str(asset.asset_type.value)
                
                # Populate metadata using information already present inside CryptoAsset
                metadata: Dict[str, Any] = {
                    "algorithm": asset.algorithm,
                    "language": asset.language,
                    "file_path": str(asset.file_path) if asset.file_path else None,
                    "line_number": asset.line_number,
                    "severity": asset.severity.value if asset.severity else None,
                    "confidence": asset.confidence
                }
                
                # Merge any existing deeper metadata from the asset
                if asset.metadata:
                    metadata.update(asset.metadata)
                    
                # Clean up None values for a pristine metadata payload
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                node = GraphNode(
                    node_type=asset.asset_type.value,
                    label=label,
                    metadata=metadata
                )
                
                # Step 5: Insert every GraphNode into CryptoGraph using add_node()
                graph.add_node(node)
                
        # Step 6: Return the graph containing only nodes. Relationships postponed to Sprint 12.
        return graph
