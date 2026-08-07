import time

from app.benchmark.baseline import Baseline
from app.benchmark.benchmark_result import BenchmarkPrediction, BenchmarkResult
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset


class GraphCentralityBaseline(Baseline):
    """
    Calculates in-degree graph centrality directly from the topological edges.
    Assumes highly connected cryptographic nodes represent a higher risk surface.
    No GNN logic used.
    """

    def initialize(self) -> None:
        pass

    def get_name(self) -> str:
        return "graph_centrality"

    def get_version(self) -> str:
        return "1.0.0"

    def predict(self, dataset: TrainingDataset, graph: CryptoGraph) -> BenchmarkResult:
        start_time = time.perf_counter()

        # Calculate in-degree centrality manually using edges
        in_degrees = {node_id: 0 for node_id in graph.nodes.keys()}
        for edge in graph.edges:
            target_str = str(edge.target_node)
            if target_str in in_degrees:
                in_degrees[target_str] += 1

        # Map centrality to 4 classes by sorting nodes
        # Top 10% = CRITICAL (3)
        # Next 20% = HIGH (2)
        # Next 30% = MEDIUM (1)
        # Bottom 40% = LOW (0)

        sorted_degrees = sorted(in_degrees.items(), key=lambda item: item[1], reverse=True)
        total = len(sorted_degrees)

        c3_bound = int(total * 0.10)
        c2_bound = c3_bound + int(total * 0.20)
        c1_bound = c2_bound + int(total * 0.30)

        predictions = []
        for idx, (node_id_str, _degree) in enumerate(sorted_degrees):
            if idx < c3_bound:
                pred_class = 3
            elif idx < c2_bound:
                pred_class = 2
            elif idx < c1_bound:
                pred_class = 1
            else:
                pred_class = 0

            predictions.append(
                BenchmarkPrediction(
                    node_id=graph.nodes[node_id_str].node_id,
                    predicted_class=pred_class,
                    confidence_score=None,  # Topological split, no statistical probability
                )
            )

        execution_time = (time.perf_counter() - start_time) * 1000

        return BenchmarkResult(
            project_id=dataset.project_id,
            baseline_name=self.get_name(),
            model_version=self.get_version(),
            execution_time_ms=execution_time,
            predictions=predictions,
        )
