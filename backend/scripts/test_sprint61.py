import os
import sys
import uuid
import logging
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset
from app.benchmark.baseline_registry import BaselineRegistry
from app.benchmark.benchmark_runner import BenchmarkRunner
from app.benchmark.benchmark_config import BenchmarkConfig

# Import baselines to register them
from app.benchmark.baselines.rule_based_baseline import RuleBasedBaseline
from app.benchmark.baselines.graph_centrality_baseline import GraphCentralityBaseline
from app.benchmark.baselines.random_baseline import RandomBaseline

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class MockNode:
    def __init__(self, nid):
        self.node_id = nid
        self.metadata = {"risk_score": 50}
        from app.models.crypto_asset import Severity, AssetType
        self.severity = Severity.MEDIUM
        self.asset_type = AssetType.KEY
        self.algorithm = "RSA"

class MockEdge:
    def __init__(self, src, tgt):
        self.source_node = src
        self.target_node = tgt

def test_sprint61():
    logging.info("Testing Sprint 61 Benchmark Framework...")
    
    # 1. Register baselines
    BaselineRegistry.register("rule_based", RuleBasedBaseline)
    BaselineRegistry.register("graph_centrality", GraphCentralityBaseline)
    BaselineRegistry.register("random", RandomBaseline)
    
    # 2. Setup mock data
    id1, id2, id3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    
    dataset = TrainingDataset(
        project_id="test_benchmark_proj",
        total_nodes=3,
        total_edges=2,
        node_features=[[1.0, 0.0, 0.5], [0.0, 1.0, 0.2], [0.0, 0.0, 1.0]],
        edge_index=[(0, 1), (1, 2)],
        node_labels=[] 
    )
    
    graph = CryptoGraph()
    graph.nodes = {str(id1): MockNode(id1), str(id2): MockNode(id2), str(id3): MockNode(id3)}
    graph.edges = [MockEdge(id1, id2), MockEdge(id2, id3)]
    
    # 3. Run Benchmark
    config = BenchmarkConfig(output_directory="backend/outputs/benchmark")
    runner = BenchmarkRunner(config)
    
    results = runner.run(dataset, graph)
    
    # We expect 4 results if GATv2 is successfully loaded (3 baselines + 1 ML model).
    # If GATv2 inference fails due to a missing checkpoint locally, it will safely skip.
    baseline_names = [res.baseline_name for res in results]
    assert "rule_based" in baseline_names, "Rule-based baseline failed."
    assert "graph_centrality" in baseline_names, "Centrality baseline failed."
    assert "random" in baseline_names, "Random baseline failed."
    
    for res in results:
        assert res.prediction_count == 3, f"{res.baseline_name} failed to predict all nodes."
        
    logging.info("All Sprint 61 Benchmark Framework tests passed successfully!")

if __name__ == "__main__":
    test_sprint61()
