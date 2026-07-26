import json
from typing import Dict, Any
from app.explainability.explanation_result import ExplanationResult

class ExplanationReport:
    """
    Generates human-readable and machine-readable reports from GNNExplainer outputs.
    """
    @staticmethod
    def generate_json(result: ExplanationResult) -> str:
        """
        Exports the exact model state deterministically for API consumption.
        """
        return result.model_dump_json(indent=2)
        
    @staticmethod
    def generate_markdown(result: ExplanationResult) -> str:
        """
        Generates a human-readable summary of the Neural Network's logic.
        """
        lines = [
            f"# XAI Report: Node {result.node_id}",
            f"**Project ID:** {result.project_id}",
            f"**Predicted Class:** {result.predicted_class}",
            f"**Confidence:** {result.prediction_probability:.2%}",
            "",
            "## Influential Features",
            "The model heavily relied on the following features of this node to make its decision:"
        ]
        
        if not result.important_features:
            lines.append("- *No specific features crossed the importance threshold.*")
        else:
            for feat in result.important_features:
                score = result.feature_scores.get(f"feature_{feat}", 0.0)
                lines.append(f"- **Feature {feat}** (Weight: {score:.4f})")
                
        lines.extend([
            "",
            "## Influential Edges",
            "The model heavily relied on the following neighborhood relationships:"
        ])
        
        if not result.important_edges:
            lines.append("- *No specific edges crossed the importance threshold.*")
        else:
            for u, v in result.important_edges:
                score = result.edge_scores.get(f"{u}_{v}", 0.0)
                lines.append(f"- Edge **{u} -> {v}** (Weight: {score:.4f})")
                
        lines.extend([
            "",
            f"*Generated at: {result.generation_timestamp}*"
        ])
        
        return "\n".join(lines)
