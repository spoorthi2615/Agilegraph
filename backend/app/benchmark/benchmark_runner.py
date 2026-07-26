import time
import logging
from typing import List

from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset
from app.benchmark.benchmark_config import BenchmarkConfig
from app.benchmark.benchmark_result import BenchmarkResult
from app.benchmark.baseline_registry import BaselineRegistry
from app.benchmark.benchmark_report import BenchmarkReport
from app.ml.inference.inference_service import InferenceService
from app.ml.inference.inference_config import InferenceConfig
from app.benchmark.benchmark_result import BenchmarkPrediction

class BenchmarkRunner:
    """
    Orchestrator for comparing the GATv2 model against all registered deterministic baselines.
    Executes all predictors and logs results to the reporting engine without evaluating them.
    """
    def __init__(self, config: BenchmarkConfig = None):
        self.config = config or BenchmarkConfig()
        self.report_engine = BenchmarkReport(self.config)
        
        # Isolate GATv2 ML inside inference service
        # Set to CPU by default for fairness when comparing latency against standard python baselines
        inf_config = InferenceConfig(device="cpu") 
        self.inference_service = InferenceService(inf_config)
        
    def run(self, dataset: TrainingDataset, graph: CryptoGraph) -> List[BenchmarkResult]:
        results: List[BenchmarkResult] = []
        
        if not dataset.node_features:
            logging.warning("Empty dataset. Skipping benchmark execution.")
            return results
            
        # 1. Instantiate Registered Baselines safely
        baselines_to_run = []
        for name in self.config.enabled_baselines:
            try:
                baselines_to_run.append(BaselineRegistry.instantiate(name))
            except KeyError:
                logging.error(f"Failed to instantiate baseline {name}. Ensure it is registered.")
                
        # Initialize
        for b in baselines_to_run:
            b.initialize()
            
        # Execute Deterministic Baselines
        for baseline in baselines_to_run:
            logging.info(f"Executing baseline: {baseline.get_name()}")
            try:
                res = baseline.predict(dataset, graph)
                results.append(res)
            except Exception as e:
                logging.error(f"Baseline {baseline.get_name()} failed during prediction: {str(e)}")
                
        # 2. Execute AgileGraph ML (GATv2)
        logging.info("Executing AgileGraph GATv2 ML Inference")
        try:
            start_time = time.perf_counter()
            ml_pred_result = self.inference_service.predict(dataset, graph)
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # Map Inference PredictionResult to BenchmarkResult for architectural consistency
            ml_predictions = [
                BenchmarkPrediction(
                    node_id=p.node_id,
                    predicted_class=p.predicted_class,
                    confidence_score=p.confidence_score
                )
                for p in ml_pred_result.predictions
            ]
            
            gat_result = BenchmarkResult(
                project_id=dataset.project_id,
                baseline_name="agilegraph_gatv2",
                model_version=ml_pred_result.model_version,
                execution_time_ms=execution_time,
                predictions=ml_predictions
            )
            results.append(gat_result)
        except Exception as e:
            logging.error(f"AgileGraph ML Inference failed: {str(e)}")
            
        # 3. Export Reports
        if results:
            self.report_engine.generate(results)
            logging.info(f"Benchmark execution complete. Reports saved to {self.config.output_directory}")
            
        return results
