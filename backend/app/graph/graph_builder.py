import logging
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID

from pydantic import ValidationError

from app.models.crypto_asset import CryptoAsset
from app.models.crypto_graph import CryptoGraph
from app.models.graph_edge import GraphEdge
from app.models.graph_node import GraphNode
from app.models.project_analysis import ProjectAnalysisResult

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    FILE = "FILE"


class EdgeType(str, Enum):
    CONTAINS = "CONTAINS"
    USES = "USES"


class GraphBuilder:
    """
    Transforms a ProjectAnalysisResult into an in-memory CryptoGraph.
    Responsible strictly for structural mapping, devoid of scanning or traversal logic.
    """

    @staticmethod
    def build_graph(
        analysis_result: ProjectAnalysisResult, dependency_map: Dict[str, List[str]] = None
    ) -> CryptoGraph:
        """
        Converts the results of the orchestration pipeline into a graph.
        Currently, this intentionally generates only nodes, deferring relationship creation.

        Args:
            analysis_result (ProjectAnalysisResult): The aggregated output from all scanners.

        Returns:
            CryptoGraph: The in-memory graph representation.
        """
        graph = CryptoGraph()

        if dependency_map is None:
            dependency_map = {}

        # Temporary local cache for file nodes: file_path -> file_node_id
        file_cache: Dict[str, UUID] = {}

        # Temporary local cache for dependencies: package_name.lower() -> dependency_node_id
        dependency_cache: Dict[str, UUID] = {}

        # Step 2: Iterate through every ScannerResult
        for scanner_result in analysis_result.scanner_results:

            # Step 3: Iterate through every finding contained inside each ScannerResult
            for finding_dict in scanner_result.findings:
                # Limitation Note: findings are currently stored as dictionaries due to
                # ScannerResult flexibility requirements. We rehydrate them to CryptoAssets.
                try:
                    asset = CryptoAsset(**finding_dict)
                except ValidationError as e:
                    logger.error(
                        f"Skipping malformed finding from scanner '{scanner_result.scanner_name}': {str(e)}"
                    )
                    continue

                # 1. Determine file_path and create/cache the FILE node if it doesn't exist
                # Use .as_posix() to ensure cross-platform normalization (converts \ to /)
                file_path_str = asset.file_path.as_posix() if asset.file_path else "unknown_file"

                if file_path_str not in file_cache:
                    # Use filename as label, full path in metadata
                    file_label = asset.file_path.name if asset.file_path else "unknown_file"

                    file_metadata = {"file_path": file_path_str}
                    if asset.language:
                        file_metadata["language"] = asset.language

                    file_node = GraphNode(
                        node_type=NodeType.FILE.value, label=file_label, metadata=file_metadata
                    )

                    graph.add_node(file_node)
                    file_cache[file_path_str] = file_node.node_id

                # Step 4: Convert every CryptoAsset into one GraphNode

                # Label must use ONLY the algorithm name
                label = asset.algorithm if asset.algorithm else str(asset.asset_type.value)

                # Populate metadata using information already present inside CryptoAsset
                metadata: Dict[str, Any] = {
                    "algorithm": asset.algorithm,
                    "language": asset.language,
                    "file_path": file_path_str if asset.file_path else None,
                    "line_number": asset.line_number,
                    "severity": asset.severity.value if asset.severity else None,
                    "confidence": asset.confidence,
                }

                # Merge any existing deeper metadata from the asset
                if asset.metadata:
                    metadata.update(asset.metadata)

                # Clean up None values for a pristine metadata payload
                metadata = {k: v for k, v in metadata.items() if v is not None}

                asset_node = GraphNode(
                    node_type=asset.asset_type.value, label=label, metadata=metadata
                )

                # Step 5: Insert every GraphNode into CryptoGraph using add_node()
                graph.add_node(asset_node)

                # Cache DEPENDENCY nodes for later relationship construction
                if asset.asset_type.value == "DEPENDENCY":
                    dependency_cache[asset.algorithm.lower()] = asset_node.node_id

                # Step 6: Create GraphEdge FILE -> CONTAINS -> CRYPTO_ASSET
                file_node_id = file_cache[file_path_str]
                edge = GraphEdge(
                    source_node=file_node_id,
                    target_node=asset_node.node_id,
                    edge_type=EdgeType.CONTAINS.value,
                    metadata={},
                )

                graph.add_edge(edge)

        # Step 7: Generate USES relationships based strictly on provided telemetry
        for file_path_str, imported_packages in dependency_map.items():
            if file_path_str not in file_cache:
                continue

            file_node_id = file_cache[file_path_str]
            for pkg in imported_packages:
                if pkg in dependency_cache:
                    edge = GraphEdge(
                        source_node=file_node_id,
                        target_node=dependency_cache[pkg],
                        edge_type=EdgeType.USES.value,
                        metadata={},
                    )
                    graph.add_edge(edge)

        return graph
