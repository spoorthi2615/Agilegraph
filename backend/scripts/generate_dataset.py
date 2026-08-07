import csv
import json
import logging
import os

# Adjust python path to be able to import app
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph.graph_builder import GraphBuilder
from app.models.crypto_asset import CryptoAsset
from app.scanners.scanner_registry import get_default_registry
from app.services.dataset_processing_service import DatasetProcessingService
from app.services.dependency_mapping_service import DependencyMappingService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.label_generation_service import LabelGenerationService
from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.services.weak_supervision_service import WeakSupervisionService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINING_DIR = os.path.join(BACKEND_DIR, "data", "training")
OUTPUTS_DIR = os.path.join(BACKEND_DIR, "outputs")

GRAPHS_DIR = os.path.join(OUTPUTS_DIR, "graphs")
DATASETS_DIR = os.path.join(OUTPUTS_DIR, "datasets")
STATS_DIR = os.path.join(OUTPUTS_DIR, "statistics")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "reports")


def setup_directories():
    for d in [GRAPHS_DIR, DATASETS_DIR, STATS_DIR, REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)


def process_repositories():
    registry = get_default_registry()
    analysis_service = ProjectAnalysisService(registry)

    summary_stats = []
    failed_repos = []

    # Track overall metrics
    total_files = 0
    total_assets = 0
    total_nodes = 0
    total_edges = 0
    total_risky = 0
    total_low_risk = 0

    for lang in ["java", "python", "go"]:
        lang_dir = os.path.join(TRAINING_DIR, lang)
        if not os.path.exists(lang_dir):
            continue

        for repo_name in os.listdir(lang_dir):
            repo_path = Path(os.path.join(lang_dir, repo_name))
            if not repo_path.is_dir():
                continue

            logging.info(f"Processing {repo_name} ({lang})...")

            try:
                # 1. Traverse and Scan
                project_id = f"{lang}_{repo_name}"
                analysis_result = analysis_service.analyze_project(project_id, repo_path)

                # Apply Risk Engine
                for scanner_result in analysis_result.scanner_results:
                    assets = [CryptoAsset(**finding) for finding in scanner_result.findings]
                    scored_assets = RiskScoringService.score_assets(assets)
                    scanner_result.findings = [
                        asset.model_dump(mode="json") for asset in scored_assets
                    ]

                # Map dependencies
                dependency_map = DependencyMappingService.map_dependencies(repo_path)

                # 2. Build CryptoGraph
                graph = GraphBuilder.build_graph(analysis_result, dependency_map)

                # 3. Generate ML Dataset
                dataset = DatasetProcessingService.process_graph(analysis_result, graph)
                dataset = FeatureEngineeringService.expand_features(dataset, graph)
                dataset = LabelGenerationService.generate_labels(dataset, graph)
                dataset = WeakSupervisionService.generate_pseudo_labels(dataset, graph)

                # Calculate simple stats for this repo
                crypto_assets = sum(len(res.findings) for res in analysis_result.scanner_results)

                risky_assets = sum(
                    1
                    for res in analysis_result.scanner_results
                    for f in res.findings
                    if float(f.get("risk_score", 0)) >= 0.5
                )
                low_risk_assets = crypto_assets - risky_assets

                stats = {
                    "repository": repo_name,
                    "language": lang,
                    "files_scanned": 0,
                    "crypto_assets": crypto_assets,
                    "dependencies": 0,  # Could be calculated from graph, leaving default
                    "certificates": 0,
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "risky_assets": risky_assets,
                    "low_risk_assets": low_risk_assets,
                }

                # Calculate asset breakdowns
                deps_count = 0
                certs_count = 0
                for res in analysis_result.scanner_results:
                    for f in res.findings:
                        if f.get("asset_type") == "DEPENDENCY":
                            deps_count += 1
                        elif f.get("asset_type") == "CERTIFICATE":
                            certs_count += 1

                stats["dependencies"] = deps_count
                stats["certificates"] = certs_count

                summary_stats.append(stats)

                total_files += 0
                total_assets += crypto_assets
                total_nodes += len(graph.nodes)
                total_edges += len(graph.edges)
                total_risky += risky_assets
                total_low_risk += low_risk_assets

                # 4. Save Outputs
                graph_path = os.path.join(GRAPHS_DIR, f"{project_id}_graph.json")
                dataset_path = os.path.join(DATASETS_DIR, f"{project_id}_dataset.json")

                graph_dict = {
                    "nodes": [n.model_dump(mode="json") for n in graph.list_nodes()],
                    "edges": [e.model_dump(mode="json") for e in graph.list_edges()],
                }
                with open(graph_path, "w") as f:
                    json.dump(graph_dict, f, indent=2)

                with open(dataset_path, "w") as f:
                    f.write(dataset.model_dump_json(indent=2))

                logging.info(f"Successfully processed {repo_name}")

            except Exception as e:
                logging.error(f"Failed to process {repo_name}: {str(e)}")
                failed_repos.append({"repository": repo_name, "error": str(e)})

    total_repos = len(summary_stats)

    consolidated = {
        "summary": {
            "total_repositories_scanned": total_repos,
            "total_files_scanned": total_files,
            "total_crypto_assets": total_assets,
            "total_graph_nodes": total_nodes,
            "total_graph_edges": total_edges,
            "total_risky_assets": total_risky,
            "total_low_risk_assets": total_low_risk,
        },
        "repositories": summary_stats,
    }

    # Save JSON Summary
    json_summary_path = os.path.join(STATS_DIR, "dataset_summary.json")
    with open(json_summary_path, "w") as f:
        json.dump(consolidated, f, indent=2)

    # Save CSV Summary
    csv_summary_path = os.path.join(STATS_DIR, "dataset_summary.csv")
    if summary_stats:
        with open(csv_summary_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=summary_stats[0].keys())
            writer.writeheader()
            writer.writerows(summary_stats)

    # Save Markdown Report
    report_path = os.path.join(REPORTS_DIR, "execution_report.md")
    with open(report_path, "w") as f:
        f.write("# Phase 6: Experimental Dataset Generation Report\n\n")
        f.write(f"**Successfully Processed:** {total_repos} repositories\n")
        f.write(f"**Failed:** {len(failed_repos)} repositories\n\n")

        if failed_repos:
            f.write("## Failures\n")
            for fail in failed_repos:
                f.write(f"- **{fail['repository']}**: {fail['error']}\n")

        f.write("\n## Output Locations\n")
        f.write(f"- **Graphs:** `{GRAPHS_DIR}`\n")
        f.write(f"- **Datasets:** `{DATASETS_DIR}`\n")
        f.write(f"- **Statistics:** `{STATS_DIR}`\n")

    logging.info("Dataset generation pipeline complete.")


if __name__ == "__main__":
    setup_directories()
    process_repositories()
