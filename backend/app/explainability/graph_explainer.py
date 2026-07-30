import logging
import torch

try:
    from torch_geometric.explain import Explainer, GNNExplainer
except ImportError:
    Explainer = None
    GNNExplainer = None

from app.explainability.explainer_config import ExplainerConfig
from app.explainability.explanation_result import ExplanationResult

logger = logging.getLogger(__name__)

class GraphExplainer:
    """
    Core engine for XAI integration. Wraps PyG's GNNExplainer algorithm.
    """
    def __init__(self, config: ExplainerConfig):
        self.config = config
        
    def explain_node(
        self, 
        model: torch.nn.Module, 
        node_index: int, 
        x: torch.Tensor, 
        edge_index: torch.Tensor, 
        project_id: str
    ) -> ExplanationResult:
        """
        Executes the GNNExplainer on the target node.
        Translates raw tensor weights into the immutable ExplanationResult model.
        """
        if Explainer is None:
            logger.warning("torch_geometric.explain is not installed. Returning empty explanation.")
            return ExplanationResult(
                project_id=project_id,
                node_id=node_index,
                predicted_class=-1,
                prediction_probability=0.0
            )
            
        # Initialize PyG Explainer
        explainer = Explainer(
            model=model,
            algorithm=GNNExplainer(epochs=self.config.epochs, lr=self.config.lr),
            explanation_type='model',
            node_mask_type='attributes',
            edge_mask_type='object',
            model_config=dict(
                mode='multiclass_classification',
                task_level='node',
                return_type=self.config.return_type,
            ),
        )
        
        # Get Model Prediction
        model.eval()
        with torch.no_grad():
            out = model(x, edge_index)
            if self.config.return_type == 'log_prob':
                probs = torch.exp(out[node_index])
            else:
                probs = out[node_index]
                
            pred_class = int(probs.argmax(dim=-1).item())
            pred_prob = float(probs.max().item())
            
        # Execute Explanation Mask Generation
        explanation = explainer(x, edge_index, index=node_index)
        
        # Extract Edge Importance
        edge_mask = explanation.edge_mask
        important_edges = []
        edge_scores = {}
        if edge_mask is not None:
            for i, val in enumerate(edge_mask):
                score = float(val.item())
                if score >= self.config.threshold:
                    u = int(edge_index[0, i].item())
                    v = int(edge_index[1, i].item())
                    important_edges.append((u, v))
                    edge_scores[f"{u}_{v}"] = score
                    
        # Extract Feature Importance for Target Node
        node_mask = explanation.node_mask
        important_features = []
        feature_scores = {}
        if node_mask is not None:
            target_features = node_mask[node_index]
            for i, val in enumerate(target_features):
                score = float(val.item())
                if score >= self.config.threshold:
                    important_features.append(i)
                    feature_scores[f"feature_{i}"] = score
                    
        return ExplanationResult(
            project_id=project_id,
            node_id=node_index,
            predicted_class=pred_class,
            prediction_probability=pred_prob,
            important_edges=important_edges,
            important_features=important_features,
            edge_scores=edge_scores,
            feature_scores=feature_scores
        )
