import time
from app.benchmark.baseline import Baseline
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset
from app.benchmark.benchmark_result import BenchmarkResult, BenchmarkPrediction
from app.services.risk_scoring_service import RiskScoringService
from app.models.crypto_asset import Severity

class RuleBasedBaseline(Baseline):
    """
    Deterministic rule-based baseline utilizing the heuristic RiskScoringService.
    Does not use machine learning.
    """
    def initialize(self) -> None:
        pass

    def get_name(self) -> str:
        return "rule_based"
        
    def get_version(self) -> str:
        return "1.0.0"

    def predict(self, dataset: TrainingDataset, graph: CryptoGraph) -> BenchmarkResult:
        start_time = time.perf_counter()
        
        nodes_list = list(graph.nodes.values())
        
        # Re-score purely based on heuristics
        scored_nodes = RiskScoringService.score_assets(nodes_list)
        
        # Mapping Severity Enum to Integers exactly as the GATv2 model expects
        severity_mapping = {
            Severity.LOW: 0,
            Severity.MEDIUM: 1,
            Severity.HIGH: 2,
            Severity.CRITICAL: 3
        }
        
        predictions = []
        for node in scored_nodes:
            predicted_class = severity_mapping.get(node.severity, 0)
            
            # Heuristic score is 0-100, normalize as a 'confidence' proxy
            confidence = float(node.metadata.get("risk_score", 0)) / 100.0
            
            predictions.append(BenchmarkPrediction(
                node_id=node.node_id,
                predicted_class=predicted_class,
                confidence_score=confidence
            ))
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        return BenchmarkResult(
            project_id=dataset.project_id,
            baseline_name=self.get_name(),
            model_version=self.get_version(),
            execution_time_ms=execution_time,
            predictions=predictions
        )
