import csv
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Tuple

import numpy as np

from app.benchmark.benchmark_config import BenchmarkConfig
from app.benchmark.benchmark_runner import BenchmarkRunner
from app.benchmark.execution.execution_result import ExecutionResult
from app.benchmark.execution.execution_statistics import (
    BaselineStatistics,
    ExperimentStatistics,
    MetricStats,
)
from app.benchmark.execution.experiment_config import ExperimentConfig
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset

logger = logging.getLogger(__name__)


class BenchmarkExecutor:
    """
    Orchestrates macro-experiments across datasets, collects raw predictions from BenchmarkRunner,
    and calculates mathematically rigorous performance metrics without heavy external dependencies.
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config

        # Override inner runner config to avoid spamming the local output directory
        runner_config = BenchmarkConfig(
            enabled_baselines=self.config.enabled_baselines,
            output_directory=os.path.join(self.config.output_directory, "raw_predictions"),
        )
        self.runner = BenchmarkRunner(runner_config)

        if not os.path.exists(self.config.output_directory):
            os.makedirs(self.config.output_directory)

    def execute_experiment(
        self, datasets: List[Tuple[TrainingDataset, CryptoGraph]]
    ) -> ExperimentStatistics:
        """
        Runs the benchmark sequence across all provided datasets and returns aggregate statistics.
        """
        all_results: List[ExecutionResult] = []

        for dataset, graph in datasets:
            if self.config.dataset_ids and dataset.project_id not in self.config.dataset_ids:
                continue

            # Filter nodes that have valid ground truth labels (-1 implies unlabeled)
            valid_indices = [i for i, label in enumerate(dataset.node_labels) if label != -1]
            if not valid_indices:
                logger.warning(
                    f"Dataset {dataset.project_id} has no ground truth labels. Skipping evaluation."
                )
                continue

            # 1. Run raw predictions
            benchmark_results = self.runner.run(dataset, graph)

            # 2. Map Ground Truths to UUIDs for exact alignment
            sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))
            ground_truth_map = {
                sorted_nodes[i].node_id: dataset.node_labels[i] for i in valid_indices
            }

            # 3. Calculate mathematical metrics for each baseline manually
            for b_result in benchmark_results:
                y_true = []
                y_pred = []

                # Align predictions
                pred_map = {p.node_id: p.predicted_class for p in b_result.predictions}

                for node_id, true_label in ground_truth_map.items():
                    if node_id in pred_map:
                        y_true.append(true_label)
                        y_pred.append(pred_map[node_id])

                if not y_true:
                    continue

                # Compute Manual Metrics for Classes 0, 1, 2, 3
                num_classes = 4
                cm = [[0] * num_classes for _ in range(num_classes)]
                correct = 0
                total = len(y_true)

                for t, p in zip(y_true, y_pred, strict=False):
                    if 0 <= t < num_classes and 0 <= p < num_classes:
                        cm[t][p] += 1
                        if t == p:
                            correct += 1

                acc = correct / total if total > 0 else 0.0

                precisions, recalls, f1s, supports = [], [], [], []

                for i in range(num_classes):
                    tp = cm[i][i]
                    fp = sum(cm[j][i] for j in range(num_classes)) - tp
                    fn = sum(cm[i][j] for j in range(num_classes)) - tp

                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                    f1 = (
                        (2 * precision * recall) / (precision + recall)
                        if (precision + recall) > 0
                        else 0.0
                    )
                    support = sum(cm[i])

                    precisions.append(precision)
                    recalls.append(recall)
                    f1s.append(f1)
                    supports.append(support)

                # Macro Averages (Unweighted mean)
                macro_prec = sum(precisions) / num_classes
                macro_rec = sum(recalls) / num_classes
                macro_f1 = sum(f1s) / num_classes

                # Weighted Averages (Weighted by Support)
                weighted_prec = (
                    sum(p * s for p, s in zip(precisions, supports, strict=False)) / total
                    if total > 0
                    else 0.0
                )
                weighted_rec = (
                    sum(r * s for r, s in zip(recalls, supports, strict=False)) / total
                    if total > 0
                    else 0.0
                )
                weighted_f1 = (
                    sum(f * s for f, s in zip(f1s, supports, strict=False)) / total
                    if total > 0
                    else 0.0
                )

                exec_res = ExecutionResult(
                    project_id=dataset.project_id,
                    baseline_name=b_result.baseline_name,
                    accuracy=acc,
                    macro_precision=macro_prec,
                    macro_recall=macro_rec,
                    macro_f1=macro_f1,
                    weighted_precision=weighted_prec,
                    weighted_recall=weighted_rec,
                    weighted_f1=weighted_f1,
                    execution_time_ms=b_result.execution_time_ms,
                    prediction_count=len(y_pred),
                    support=len(y_true),
                    confusion_matrix=cm,
                )
                all_results.append(exec_res)

        # 4. Compute Aggregate Statistics
        stats = self._compute_statistics(all_results)

        # 5. Export Reports
        if all_results:
            self._export_reports(all_results, stats)

        return stats

    def _compute_statistics(self, results: List[ExecutionResult]) -> ExperimentStatistics:
        baseline_groups = defaultdict(list)
        for res in results:
            baseline_groups[res.baseline_name].append(res)

        stats_dict = {}
        for b_name, b_results in baseline_groups.items():

            def calc_metric(metric_name: str) -> MetricStats:
                values = [getattr(r, metric_name) for r in b_results]
                return MetricStats(
                    average=float(np.mean(values)),
                    std_dev=float(np.std(values)),
                    min_val=float(np.min(values)),
                    max_val=float(np.max(values)),
                )

            b_stat = BaselineStatistics(
                baseline_name=b_name,
                total_repositories_tested=len(b_results),
                accuracy=calc_metric("accuracy"),
                macro_precision=calc_metric("macro_precision"),
                macro_recall=calc_metric("macro_recall"),
                macro_f1=calc_metric("macro_f1"),
                weighted_precision=calc_metric("weighted_precision"),
                weighted_recall=calc_metric("weighted_recall"),
                weighted_f1=calc_metric("weighted_f1"),
                execution_time_ms=calc_metric("execution_time_ms"),
            )
            stats_dict[b_name] = b_stat

        return ExperimentStatistics(baselines=stats_dict)

    def _export_reports(self, results: List[ExecutionResult], stats: ExperimentStatistics) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Save individual repository results to CSV
        csv_path = os.path.join(self.config.output_directory, f"experiment_results_{timestamp}.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Project",
                    "Baseline",
                    "Accuracy",
                    "Macro F1",
                    "Weighted F1",
                    "Support",
                    "Execution Time (ms)",
                ]
            )
            for res in results:
                writer.writerow(
                    [
                        res.project_id,
                        res.baseline_name,
                        f"{res.accuracy:.4f}",
                        f"{res.macro_f1:.4f}",
                        f"{res.weighted_f1:.4f}",
                        res.support,
                        f"{res.execution_time_ms:.2f}",
                    ]
                )

        # Save aggregate statistics to JSON
        json_path = os.path.join(
            self.config.output_directory, f"experiment_statistics_{timestamp}.json"
        )
        with open(json_path, "w") as f:
            json.dump(stats.model_dump(), f, indent=2)

        logger.info(f"Experiment reports saved to {self.config.output_directory}")
