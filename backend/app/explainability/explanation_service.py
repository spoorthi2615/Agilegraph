import logging

import torch

from app.explainability.explanation_report import ExplanationReport
from app.explainability.explanation_result import ExplanationResult
from app.explainability.graph_explainer import GraphExplainer

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Facade orchestrating the PyG GNNExplainer pipeline.
    Enforces strict Dependency Injection.
    """

    def __init__(self, explainer: GraphExplainer):
        self.explainer = explainer

    def generate_explanation(
        self,
        model: torch.nn.Module,
        node_index: int,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        project_id: str,
    ) -> ExplanationResult:
        """
        Runs the explainer algorithm and generates the strongly typed result.
        """
        logger.info(f"Initiating GNNExplainer for Node {node_index} in project '{project_id}'...")

        result = self.explainer.explain_node(model, node_index, x, edge_index, project_id)

        logger.info(
            f"Explanation complete. Found {len(result.important_features)} influential features and {len(result.important_edges)} influential edges."
        )
        return result

    def get_markdown_report(self, result: ExplanationResult) -> str:
        return ExplanationReport.generate_markdown(result)

    def get_json_report(self, result: ExplanationResult) -> str:
        return ExplanationReport.generate_json(result)
