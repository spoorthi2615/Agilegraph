import os
import sys
import torch
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from torch_geometric.data import Data
from app.ml.models.gatv2_model import GATv2Model
from app.ml.evaluation.evaluator import GATv2Evaluator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint59():
    logging.info("Testing Sprint 59 Evaluation Framework...")
    
    # 1. Mock Data (5 nodes, 3 features, 4 classes)
    x = torch.rand(5, 3)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long)
    
    # y contains a -1 to test filtering logic
    y = torch.tensor([0, 1, 2, 3, -1], dtype=torch.long)
    data = Data(x=x, edge_index=edge_index, y=y)
    
    # 2. Mock Model
    model = GATv2Model(in_dim=3, hidden_dim=8, out_dim=4, heads=2)
    
    # 3. Create Evaluator
    evaluator = GATv2Evaluator(model, device="cpu")
    
    # 4. Evaluate (this inherently tests forward pass, no_grad, metrics, roc, confusion matrix, export)
    report = evaluator.evaluate(data, dataset_version="test_mock", num_classes=4)
    
    # 5. Assertions
    # There are 4 labeled nodes (classes 0, 1, 2, 3). Unlabeled node (-1) should be filtered.
    assert len(report.per_class_metrics) == 4, "Per-class metrics failed to calculate."
    assert len(report.confusion_matrix["matrix"]) == 4, "Confusion matrix shape is incorrect."
    
    # Check outputs exist
    output_dir = "backend/outputs/evaluation"
    assert os.path.exists(output_dir), "Output directory not created."
    
    files = os.listdir(output_dir)
    assert any(f.endswith(".json") and "test_mock" in f for f in files), "JSON export failed."
    assert any(f.endswith(".csv") and "test_mock" in f for f in files), "CSV export failed."
    assert any(f.endswith(".md") and "test_mock" in f for f in files), "Markdown export failed."
    
    # Test invalid checkpoint handling
    try:
        evaluator.load_checkpoint("non_existent_file.pt")
        assert False, "Should have thrown FileNotFoundError"
    except FileNotFoundError:
        pass
        
    logging.info("All Sprint 59 Evaluation Tests Passed Successfully!")

if __name__ == "__main__":
    test_sprint59()
