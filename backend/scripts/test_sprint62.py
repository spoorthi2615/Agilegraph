import os
import sys
import logging
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph
from app.benchmark.execution.experiment_config import ExperimentConfig
from app.benchmark.execution.benchmark_executor import BenchmarkExecutor
from app.benchmark.baselines.rule_based_baseline import RuleBasedBaseline
from app.benchmark.baselines.graph_centrality_baseline import GraphCentralityBaseline
from app.benchmark.baselines.random_baseline import RandomBaseline
from app.benchmark.baseline_registry import BaselineRegistry

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def create_mock_dataset(project_id: str) -> Tuple[TrainingDataset, CryptoGraph]:
    dataset = TrainingDataset(
        project_id=project_id,
        total_nodes=4,
        total_edges=4,
        node_features=[[1.0, 0.0, 0.5], [0.0, 1.0, 0.2], [0.5, 0.5, 0.9], [0.1, 0.9, 0.1]],
        edge_index=[(0, 1), (1, 2), (2, 3), (3, 0)],
        node_labels=[0, 1, 2, 3], # Known labels for exact matching
        train_mask=[False, False, False, False],
        val_mask=[True, True, True, True]
    )
    
    graph = CryptoGraph(project_id=project_id)
    class MockNode:
        def __init__(self, nid):
            self.node_id = nid
            from app.models.crypto_asset import AssetType
            self.asset_type = AssetType.APPLICATION_CODE
            
    # Use string ids to simulate uuid
    for i in range(4):
        graph.nodes[str(i)] = MockNode(str(i))
        
    return dataset, graph

def test_sprint62():
    logging.info("Testing Sprint 62 Benchmark Execution Pipeline...")
    
    # 1. Register baselines
    BaselineRegistry.register("rule_based", RuleBasedBaseline())
    BaselineRegistry.register("graph_centrality", GraphCentralityBaseline())
    BaselineRegistry.register("random", RandomBaseline())
    
    # 2. Create mock datasets
    datasets = [
        create_mock_dataset("repo_alpha"),
        create_mock_dataset("repo_beta")
    ]
    
    # 3. Configure executor
    config = ExperimentConfig(
        dataset_ids=["repo_alpha", "repo_beta"],
        enabled_baselines=["rule_based", "graph_centrality", "random"],
        output_directory="outputs/experiments"
    )
    
    # 4. Execute
    executor = BenchmarkExecutor(config)
    stats = executor.execute_experiment(datasets)
    
    # 5. Validate Output Statistics
    assert stats is not None, "ExperimentStatistics was not generated."
    
    # Verify we collected stats for our baselines (plus gatv2)
    assert "rule_based" in stats.baselines, "Missing rule_based stats"
    assert "graph_centrality" in stats.baselines, "Missing graph_centrality stats"
    assert "random" in stats.baselines, "Missing random stats"
    assert "gatv2" in stats.baselines, "Missing gatv2 stats"
    
    rule_stats = stats.baselines["rule_based"]
    assert rule_stats.total_repositories_tested == 2, f"Expected 2 repositories tested, got {rule_stats.total_repositories_tested}"
    
    assert hasattr(rule_stats.accuracy, 'average'), "Missing accuracy average"
    assert hasattr(rule_stats.macro_f1, 'std_dev'), "Missing macro_f1 std_dev"
    
    logging.info("All Sprint 62 Benchmark Execution Framework tests passed successfully!")

if __name__ == "__main__":
    test_sprint62()
