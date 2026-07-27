import os
import torch
import logging
from pathlib import Path
from torch_geometric.data import Data

# Setup Django/FastAPI environment if needed, but we can just import the services
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.graph.graph_builder import GraphBuilder
from app.scanners.scanner_registry import get_default_registry
from app.models.crypto_asset import CryptoAsset
from app.services.dependency_mapping_service import DependencyMappingService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_corpus():
    corpus_dir = Path("backend/data/corpus")
    output_dir = Path("backend/data/tensors")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not corpus_dir.exists() or not list(corpus_dir.iterdir()):
        logging.error("Corpus directory is empty. Run fetch_github_corpus.py first.")
        return
        
    analysis_service = ProjectAnalysisService(get_default_registry())
    
    dataset = []
    
    for repo_path in corpus_dir.iterdir():
        if not repo_path.is_dir():
            continue
            
        project_id = repo_path.name
        logging.info(f"Processing repository: {project_id}")
        
        try:
            # 1. Static Analysis
            analysis_result = analysis_service.analyze_project(project_id, repo_path)
            
            # 2. Scoring
            for scanner_result in analysis_result.scanner_results:
                assets = [CryptoAsset(**finding) for finding in scanner_result.findings]
                scored_assets = RiskScoringService.score_assets(assets)
                scanner_result.findings = [asset.model_dump(mode="json") for asset in scored_assets]
                
            # 3. Dependency Mapping
            dependency_map = DependencyMappingService.map_dependencies(repo_path)
            
            # 4. Graph Building
            graph = GraphBuilder.build_graph(analysis_result, dependency_map)
            logging.info(f"Built graph for {project_id}: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # 5. Convert to PyTorch Geometric Data
            # For simplicity, we create dummy node features if embeddings aren't fully integrated yet
            # In a real run, CodeBERT would generate `x`. We'll simulate 768-dim embeddings.
            num_nodes = len(graph.nodes)
            if num_nodes == 0:
                logging.warning(f"No nodes found for {project_id}, skipping.")
                continue
                
            # Map node IDs to integers
            node_mapping = {node_id: idx for idx, node_id in enumerate(graph.nodes.keys())}
            
            # Features (x)
            x = torch.randn((num_nodes, 768), dtype=torch.float)
            
            # Edges (edge_index)
            edge_index = []
            for edge in graph.edges:
                src = node_mapping.get(edge.source_node)
                dst = node_mapping.get(edge.target_node)
                if src is not None and dst is not None:
                    edge_index.append([src, dst])
                    
            if not edge_index:
                edge_index = torch.empty((2, 0), dtype=torch.long)
            else:
                edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
                
            # Labels (y) - proxy labels derived from risk scores (0: Safe, 1: Vulnerable)
            y = torch.zeros(num_nodes, dtype=torch.long)
            for idx, (node_id, node) in enumerate(graph.nodes.items()):
                risk = node.metadata.get('risk_score', 0)
                if risk > 40:  # Arbitrary threshold for vulnerable
                    y[idx] = 1
                    
            data = Data(x=x, edge_index=edge_index, y=y)
            
            # Create train/val/test masks (80/10/10 split)
            indices = torch.randperm(num_nodes)
            train_idx = indices[:int(0.8 * num_nodes)]
            val_idx = indices[int(0.8 * num_nodes):int(0.9 * num_nodes)]
            test_idx = indices[int(0.9 * num_nodes):]
            
            train_mask = torch.zeros(num_nodes, dtype=torch.bool)
            val_mask = torch.zeros(num_nodes, dtype=torch.bool)
            test_mask = torch.zeros(num_nodes, dtype=torch.bool)
            
            train_mask[train_idx] = True
            val_mask[val_idx] = True
            test_mask[test_idx] = True
            
            data.train_mask = train_mask
            data.val_mask = val_mask
            data.test_mask = test_mask
            
            # Save tensor
            out_file = output_dir / f"{project_id}.pt"
            torch.save(data, out_file)
            logging.info(f"Saved dataset tensor for {project_id} to {out_file}")
            
            dataset.append(data)
            
        except Exception as e:
            logging.error(f"Failed to process {project_id}: {e}")
            
    # Combine into a single massive graph for training (batching) if desired, 
    # but saving individually is safer for GNN data loaders.

if __name__ == "__main__":
    process_corpus()
