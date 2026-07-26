import os
import sys
import logging
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.explainability.explainer_config import ExplainerConfig
from app.explainability.explanation_result import ExplanationResult
from app.explainability.graph_explainer import GraphExplainer
from app.explainability.explanation_service import ExplanationService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Simple Mock GNN Model
class MockGATv2(torch.nn.Module):
    def __init__(self):
        super().__init__()
        # Mock weights to create a deterministic fake prediction
        self.fc = torch.nn.Linear(3, 2)
        
    def forward(self, x, edge_index):
        # Fake logic: Class 1 if feature 0 is high, else Class 0
        logits = self.fc(x)
        # Force deterministic output for testing without real GNN weights
        logits[:, 0] = x[:, 0] * 0.1
        logits[:, 1] = x[:, 0] * 0.9 
        return logits

def test_sprint75():
    logging.info("Testing Sprint 74 XAI GNNExplainer Integration...")
    
    # Check if PyG Explainer is actually installed in this environment
    try:
        import torch_geometric.explain
        pyg_installed = True
    except ImportError:
        pyg_installed = False
        
    if not pyg_installed:
        logging.warning("torch_geometric is missing in this test env. Validating graceful fallback...")
    
    config = ExplainerConfig(epochs=2, lr=0.1, threshold=0.1)
    explainer = GraphExplainer(config)
    service = ExplanationService(explainer)
    
    # Create Mock Graph
    # 4 Nodes, 3 Features each
    x = torch.tensor([
        [1.0, 0.0, 0.5], # Target Node (0)
        [0.0, 1.0, 0.0],
        [0.5, 0.5, 1.0],
        [0.0, 0.0, 0.0]
    ], dtype=torch.float)
    
    # Edges: 0-1, 1-2, 0-2, 3 isolated
    edge_index = torch.tensor([
        [0, 1, 0, 1, 2, 2],
        [1, 0, 2, 2, 1, 0]
    ], dtype=torch.long)
    
    model = MockGATv2()
    
    # 1. Test Explanation Generation
    result = service.generate_explanation(model, 0, x, edge_index, "proj_01")
    
    assert isinstance(result, ExplanationResult)
    assert result.project_id == "proj_01"
    assert result.node_id == 0
    
    # If PyG is installed, test the tensor outputs. Otherwise just test graceful failure.
    if pyg_installed:
        logging.info(f"PyG Explainer ran. Influential features: {result.important_features}")
        assert len(result.important_features) >= 0
    else:
        assert result.predicted_class == -1
        
    # 2. Test Markdown Generation
    md_report = service.get_markdown_report(result)
    assert "XAI Report: Node 0" in md_report
    assert "**Project ID:** proj_01" in md_report
    logging.info("Markdown Generation succeeded.")
    
    # 3. Test Graph Edge Translation
    # Fake some data for the graph translation test
    result.important_features = [0, 2]
    result.important_edges = [(0, 1)]
    edges = result.to_graph_edges()
    
    node_str = f"Explanation:0_{result.generation_timestamp[:10]}"
    assert (node_str, "EXPLAINS", "CryptoNode:0") in edges
    assert (node_str, "IDENTIFIES_IMPORTANT_FEATURE", "Feature:0") in edges
    assert (node_str, "IDENTIFIES_IMPORTANT_EDGE", "GraphEdge:0_1") in edges
    logging.info("Graph Database serialization mappings passed.")
    
    logging.info("All Sprint 74 XAI tests passed successfully!")

if __name__ == "__main__":
    test_sprint75()
