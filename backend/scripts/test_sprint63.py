import os
import sys
import logging
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph
from app.experiments.ablation.ablation_config import AblationConfig
from app.experiments.ablation.ablation_runner import AblationRunner
from app.benchmark.baselines.rule_based_baseline import RuleBasedBaseline
from app.benchmark.baseline_registry import BaselineRegistry

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def create_mock_dataset(project_id: str) -> Tuple[TrainingDataset, CryptoGraph]:
    dataset = TrainingDataset(
        project_id=project_id,
        total_nodes=4,
        total_edges=4,
        node_features=[[1.0, 0.0, 0.5], [0.0, 1.0, 0.2], [0.5, 0.5, 0.9], [0.1, 0.9, 0.1]],
        edge_index=[(0, 1), (1, 2), (2, 3), (3, 0)],
        node_labels=[0, 1, 2, 3],
        train_mask=[False, False, False, False],
        val_mask=[True, True, True, True],
        metadata={
            "ablation_masks": {
                "dependencies": [0],
                "certificates": [1],
                "deterministic": [2]
            }
        }
    )
    
    graph = CryptoGraph(project_id=project_id)
    class MockNode:
        def __init__(self, nid):
            self.node_id = nid
            from app.models.crypto_asset import AssetType
            self.asset_type = AssetType.APPLICATION_CODE
            
    for i in range(4):
        graph.nodes[str(i)] = MockNode(str(i))
        
    return dataset, graph

def test_sprint63():
    logging.info("Testing Sprint 63 Ablation Study Framework...")
    
    # 1. Register baseline fallback for "Without Attention Layer"
    BaselineRegistry.register("rule_based", RuleBasedBaseline())
    
    # 2. Create mock datasets
    datasets = [create_mock_dataset("repo_ablation_test")]
    
    # 3. Load default ablation matrix
    config = AblationConfig.default_matrix()
    config.output_directory = "outputs/ablation"
    
    # 4. Execute Ablation Runner
    runner = AblationRunner(config)
    results = runner.run(datasets)
    
    # 5. Validation
    assert len(results) == 7, f"Expected 7 ablation experiments, got {len(results)}"
    
    # Check that Full Model is baseline
    assert results[0].experiment_name == "Full Model"
    assert results[0].accuracy_drop == 0.0
    
    # Check that metrics were generated
    for res in results:
        assert hasattr(res, 'accuracy'), f"Missing accuracy on {res.experiment_name}"
        assert hasattr(res, 'percentage_performance_drop'), f"Missing percentage_performance_drop on {res.experiment_name}"
        logging.info(f"{res.experiment_name} | Acc: {res.accuracy:.2f} | Drop: {res.percentage_performance_drop:.2f}%")
        
    logging.info("All Sprint 63 Ablation Study Framework tests passed successfully!")

if __name__ == "__main__":
    test_sprint63()
