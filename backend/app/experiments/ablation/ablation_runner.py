import logging
import copy
from typing import List, Tuple
from app.experiments.ablation.ablation_config import AblationConfig, AblationExperiment
from app.experiments.ablation.ablation_result import AblationResult
from app.experiments.ablation.ablation_report import AblationReport
from app.models.training_dataset import TrainingDataset
from app.models.crypto_graph import CryptoGraph
from app.benchmark.execution.benchmark_executor import BenchmarkExecutor
from app.benchmark.execution.experiment_config import ExperimentConfig

logger = logging.getLogger(__name__)

class AblationRunner:
    """
    Orchestrates the sequential testing of architecture combinations.
    """
    def __init__(self, config: AblationConfig):
        self.config = config

    def _apply_ablation(self, dataset: TrainingDataset, experiment: AblationExperiment) -> Tuple[TrainingDataset, str]:
        """
        Clones and modifies the dataset mathematically based on the toggle configuration.
        """
        ablated = copy.deepcopy(dataset)
        toggle = experiment.toggle
        
        # 1. Topology Ablation
        if not toggle.enable_graph_topology:
            ablated.edge_index = []
            
        if not toggle.enable_risk_propagation:
            # Simulate removing risk propagation by severing half the graph edges 
            # (In reality, this would sever specific directional edge types)
            ablated.edge_index = ablated.edge_index[:len(ablated.edge_index)//2]
            
        # 2. Feature Ablation (Masking out columns based on dynamic metadata map)
        ablation_masks = ablated.metadata.get("ablation_masks", {})
        
        columns_to_zero = []
        if not toggle.enable_dependencies:
            columns_to_zero.extend(ablation_masks.get("dependencies", []))
        if not toggle.enable_certificates:
            columns_to_zero.extend(ablation_masks.get("certificates", []))
        if not toggle.enable_deterministic_features:
            columns_to_zero.extend(ablation_masks.get("deterministic", []))
            
        if columns_to_zero:
            for row in ablated.node_features:
                for col in columns_to_zero:
                    if col < len(row):
                        row[col] = 0.0
                        
        # 3. Model Swap for Attention Layer Ablation
        baseline_override = "gatv2"
        if not toggle.enable_attention_layer:
            # Replace GNN attention architecture with flat heuristic equivalent
            baseline_override = "rule_based"
            
        return ablated, baseline_override

    def run(self, datasets: List[Tuple[TrainingDataset, CryptoGraph]]) -> List[AblationResult]:
        results = []
        full_model_f1 = None
        full_model_acc = None
        
        for exp in self.config.experiments:
            logger.info(f"Running Ablation Experiment: {exp.name}")
            
            ablated_datasets = []
            baseline_target = "gatv2"
            
            for d, g in datasets:
                if self.config.dataset_ids and d.project_id not in self.config.dataset_ids:
                    continue
                ablated_d, b_target = self._apply_ablation(d, exp)
                ablated_datasets.append((ablated_d, g))
                baseline_target = b_target
                
            if not ablated_datasets:
                continue
                
            # Execute standard benchmark executor for this specific architectural toggle
            exec_config = ExperimentConfig(
                enabled_baselines=[baseline_target],
                output_directory=os.path.join(self.config.output_directory, "raw")
            )
            executor = BenchmarkExecutor(exec_config)
            stats = executor.execute_experiment(ablated_datasets)
            
            # Extract aggregate metrics for the baseline
            b_stats = stats.baselines.get(baseline_target)
            if not b_stats:
                logger.warning(f"No statistics generated for {baseline_target}")
                continue
                
            acc = b_stats.accuracy.average
            macro_f1 = b_stats.macro_f1.average
            weighted_f1 = b_stats.weighted_f1.average
            exec_time = b_stats.execution_time_ms.average
            
            # Track Full Model baseline for delta computation
            if exp.name == "Full Model":
                full_model_f1 = macro_f1
                full_model_acc = acc
                acc_drop = 0.0
                f1_drop = 0.0
                perf_drop = 0.0
            else:
                acc_drop = (full_model_acc - acc) if full_model_acc else 0.0
                f1_drop = (full_model_f1 - macro_f1) if full_model_f1 else 0.0
                perf_drop = (f1_drop / full_model_f1 * 100) if full_model_f1 and full_model_f1 > 0 else 0.0
                
            res = AblationResult(
                experiment_name=exp.name,
                accuracy=acc,
                macro_precision=b_stats.macro_precision.average,
                macro_recall=b_stats.macro_recall.average,
                macro_f1=macro_f1,
                weighted_precision=b_stats.weighted_precision.average,
                weighted_recall=b_stats.weighted_recall.average,
                weighted_f1=weighted_f1,
                execution_time_ms=exec_time,
                accuracy_drop=acc_drop,
                macro_f1_drop=f1_drop,
                percentage_performance_drop=perf_drop
            )
            results.append(res)
            
        AblationReport.generate(results, self.config.output_directory)
        return results
