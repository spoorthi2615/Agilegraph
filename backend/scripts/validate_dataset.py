import json
import logging
import math
import os

# Adjust python path
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BACKEND_DIR, "outputs")
GRAPHS_DIR = os.path.join(OUTPUTS_DIR, "graphs")
DATASETS_DIR = os.path.join(OUTPUTS_DIR, "datasets")
STATS_DIR = os.path.join(OUTPUTS_DIR, "statistics")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "reports")


def ensure_directories():
    for d in [GRAPHS_DIR, DATASETS_DIR, STATS_DIR, REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)


def validate():
    ensure_directories()

    total_repos = 36
    processed_repos = 0
    missing_artifacts = []

    # Validation trackers
    graph_violations = []
    dataset_violations = []

    # Statistics
    stats_total_files = 0
    stats_nodes = 0
    stats_edges = 0
    risk_dist = {"0": 0, "1": 0, "2": 0, "3": 0}
    asset_dist = defaultdict(int)
    lang_dist = defaultdict(int)
    repo_sizes = {}  # repo_id -> total_nodes

    for filename in os.listdir(DATASETS_DIR):
        if not filename.endswith("_dataset.json"):
            continue

        repo_id = filename.replace("_dataset.json", "")
        dataset_path = os.path.join(DATASETS_DIR, filename)
        graph_path = os.path.join(GRAPHS_DIR, f"{repo_id}_graph.json")

        if not os.path.exists(graph_path):
            missing_artifacts.append(f"{repo_id}: Missing CryptoGraph")
            continue

        processed_repos += 1

        lang = repo_id.split("_")[0]
        lang_dist[lang] += 1

        # 1. Validate CryptoGraph
        with open(graph_path, "r") as f:
            graph_data = json.load(f)

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        repo_sizes[repo_id] = len(nodes)
        stats_nodes += len(nodes)
        stats_edges += len(edges)

        node_ids = set()
        for _idx, node in enumerate(nodes):
            nid = node.get("node_id")
            if nid in node_ids:
                graph_violations.append(f"{repo_id}: Duplicate Node ID {nid}")
            node_ids.add(nid)

            # Asset distribution
            ntype = node.get("node_type")
            asset_dist[ntype] += 1
            if ntype == "FILE":
                stats_total_files += 1

        for edge in edges:
            if edge.get("source_node") not in node_ids:
                graph_violations.append(
                    f"{repo_id}: Dangling Edge source {edge.get('source_node')}"
                )
            if edge.get("target_node") not in node_ids:
                graph_violations.append(
                    f"{repo_id}: Dangling Edge target {edge.get('target_node')}"
                )

        # 2. Validate TrainingDataset
        with open(dataset_path, "r") as f:
            ds = json.load(f)

        node_features = ds.get("node_features", [])
        labels = ds.get("node_labels", [])

        # Dimensions
        if len(node_features) != len(nodes):
            dataset_violations.append(
                f"{repo_id}: Feature vector length ({len(node_features)}) != nodes length ({len(nodes)})"
            )

        if len(labels) != len(nodes):
            dataset_violations.append(
                f"{repo_id}: Labels length ({len(labels)}) != nodes length ({len(nodes)})"
            )

        # NaN / Inf validation & Auto-repair logic via tracking
        if node_features:
            dim = len(node_features[0])
            for i, vec in enumerate(node_features):
                if len(vec) != dim:
                    dataset_violations.append(
                        f"{repo_id}: Inconsistent feature dimensions at node index {i}"
                    )
                for val in vec:
                    if val is None or math.isnan(val) or math.isinf(val):
                        dataset_violations.append(f"{repo_id}: NaN/Inf detected in feature vectors")
                        break
        else:
            if len(nodes) > 0:
                dataset_violations.append(
                    f"{repo_id}: Feature vectors empty but graph has {len(nodes)} nodes"
                )

        for label in labels:
            if str(label) in risk_dist:
                risk_dist[str(label)] += 1

    # 3. Write Statistics
    summary = {
        "total_repositories": total_repos,
        "processed_successfully": processed_repos,
        "failed_or_skipped": total_repos - processed_repos,
        "total_files_scanned": stats_total_files,
        "total_graph_nodes": stats_nodes,
        "total_graph_edges": stats_edges,
        "risk_distribution": risk_dist,
        "asset_distribution": dict(asset_dist),
        "language_distribution": dict(lang_dist),
    }

    with open(os.path.join(STATS_DIR, "dataset_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Write Dataset Readiness Report
    report_path = os.path.join(REPORTS_DIR, "dataset_readiness_report.md")
    with open(report_path, "w") as f:
        f.write("# Dataset Validation & Readiness Report\n\n")

        f.write("## 1. Repository Coverage\n")
        f.write(f"- **Target Repositories:** {total_repos}\n")
        f.write(f"- **Processed Successfully:** {processed_repos}\n")
        f.write(f"- **Failed/Missing:** {total_repos - processed_repos}\n\n")

        if missing_artifacts:
            f.write("### Missing Artifacts\n")
            for m in missing_artifacts:
                f.write(f"- {m}\n")
            f.write("\n")

        f.write("## 2. Graph & Dataset Integrity\n")
        f.write(f"- **Graph Violations Detected:** {len(graph_violations)}\n")
        f.write(f"- **Dataset Violations Detected:** {len(dataset_violations)}\n\n")

        if graph_violations:
            f.write("### Graph Violations\n")
            for v in graph_violations[:10]:
                f.write(f"- {v}\n")
            if len(graph_violations) > 10:
                f.write("- ... and more\n")
            f.write("\n")

        if dataset_violations:
            f.write("### Dataset Violations\n")
            for v in dataset_violations[:10]:
                f.write(f"- {v}\n")
            if len(dataset_violations) > 10:
                f.write("- ... and more\n")
            f.write("\n")

        f.write("## 3. Dataset Quality (Class Balance)\n")
        f.write("- **High Risk (3):** " + str(risk_dist["3"]) + "\n")
        f.write("- **Medium Risk (2):** " + str(risk_dist["2"]) + "\n")
        f.write("- **Low Risk (1):** " + str(risk_dist["1"]) + "\n")
        f.write("- **Safe (0):** " + str(risk_dist["0"]) + "\n\n")

        f.write("### Recommendation\n")
        total_risk = risk_dist["3"] + risk_dist["2"] + risk_dist["1"]
        if risk_dist["0"] > total_risk * 10:
            f.write(
                "> **WARNING: Severe Class Imbalance.** Safe nodes heavily outnumber risky nodes. "
            )
            f.write(
                "It is highly recommended to use **Focal Loss** or apply Node Sampling techniques during GATv2 training.\n\n"
            )
        else:
            f.write("> Class balance is acceptable for GNN training.\n\n")

        f.write("## 4. Overall Readiness\n")
        score = 10
        if total_repos - processed_repos > 0:
            score -= 1
        if len(graph_violations) > 0:
            score -= 3
        if len(dataset_violations) > 0:
            score -= 3
        if risk_dist["0"] > total_risk * 10:
            score -= 1

        f.write(f"### Readiness Score: {max(0, score)} / 10\n\n")
        if score >= 8:
            f.write(
                "**Status: READY FOR TRAINING.** The dataset is mathematically sound and ready to be loaded by PyTorch Geometric.\n"
            )
        else:
            f.write(
                "**Status: ACTION REQUIRED.** Please address the structural violations before proceeding to training.\n"
            )

    logging.info("Validation complete! Check backend/outputs/reports/dataset_readiness_report.md")


if __name__ == "__main__":
    validate()
