import time
import random
from app.benchmark.baseline import Baseline
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset
from app.benchmark.benchmark_result import BenchmarkResult, BenchmarkPrediction

class RandomBaseline(Baseline):
    """
    Stochastic prediction baseline.
    Establishes the absolute lower bound of statistical performance for comparative experiments.
    """
    def initialize(self) -> None:
        pass

    def get_name(self) -> str:
        return "random"
        
    def get_version(self) -> str:
        return "1.0.0"

    def predict(self, dataset: TrainingDataset, graph: CryptoGraph) -> BenchmarkResult:
        start_time = time.perf_counter()
        
        predictions = []
        for node in graph.nodes.values():
            predictions.append(BenchmarkPrediction(
                node_id=node.node_id,
                predicted_class=random.randint(0, 3), # 4 classes [0, 1, 2, 3]
                confidence_score=random.uniform(0.0, 1.0)
            ))
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        return BenchmarkResult(
            project_id=dataset.project_id,
            baseline_name=self.get_name(),
            model_version=self.get_version(),
            execution_time_ms=execution_time,
            predictions=predictions
        )
