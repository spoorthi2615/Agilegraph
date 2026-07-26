import os
import json
import logging
from pathlib import Path

# Adjust python path to be able to import app
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scanners.scanner_registry import get_default_registry
from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.services.dependency_mapping_service import DependencyMappingService
from app.graph.graph_builder import GraphBuilder
from app.services.dataset_processing_service import DatasetProcessingService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.label_generation_service import LabelGenerationService
from app.services.weak_supervision_service import WeakSupervisionService
from app.models.crypto_asset import CryptoAsset

from scripts.generate_dataset import (
    setup_directories, 
    TRAINING_DIR, 
    GRAPHS_DIR, 
    DATASETS_DIR
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def retry_failed():
    registry = get_default_registry()
    analysis_service = ProjectAnalysisService(registry)
    
    failed_repos = [
        ("java", "jitsi-meet"),
        ("python", "flask-security")
    ]
    
    for lang, repo_name in failed_repos:
        repo_path = Path(os.path.join(TRAINING_DIR, lang, repo_name))
        if not repo_path.is_dir():
            logging.error(f"Directory {repo_path} not found.")
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
                scanner_result.findings = [asset.model_dump(mode="json") for asset in scored_assets]
                
            # Map dependencies
            dependency_map = DependencyMappingService.map_dependencies(repo_path)
            
            # 2. Build CryptoGraph
            graph = GraphBuilder.build_graph(analysis_result, dependency_map)
            
            # 3. Generate ML Dataset
            dataset = DatasetProcessingService.process_graph(analysis_result, graph)
            dataset = FeatureEngineeringService.expand_features(dataset, graph)
            dataset = LabelGenerationService.generate_labels(dataset, graph)
            dataset = WeakSupervisionService.generate_pseudo_labels(dataset, graph)
            
            # 4. Save Outputs
            graph_path = os.path.join(GRAPHS_DIR, f"{project_id}_graph.json")
            dataset_path = os.path.join(DATASETS_DIR, f"{project_id}_dataset.json")
            
            graph_dict = {
                "nodes": [n.model_dump(mode="json") for n in graph.list_nodes()],
                "edges": [e.model_dump(mode="json") for e in graph.list_edges()]
            }
            with open(graph_path, "w") as f:
                json.dump(graph_dict, f, indent=2)
                
            with open(dataset_path, "w") as f:
                f.write(dataset.model_dump_json(indent=2))
                
            logging.info(f"Successfully processed {repo_name}")
            
        except Exception as e:
            logging.error(f"Failed to process {repo_name}: {str(e)}")

if __name__ == "__main__":
    setup_directories()
    retry_failed()
