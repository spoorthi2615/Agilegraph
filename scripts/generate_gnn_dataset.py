import os
import torch
import logging
from pathlib import Path
from torch_geometric.data import Data
from transformers import AutoTokenizer, AutoModel

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
        
    logging.info("Loading CodeBERT model...")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    codebert_model = AutoModel.from_pretrained("microsoft/codebert-base")
    codebert_model.eval()
        
    analysis_service = ProjectAnalysisService(get_default_registry())
    
    dataset = []
    
    repo_paths = [p for p in corpus_dir.iterdir() if p.is_dir()]
    num_repos = len(repo_paths)
    
    # Calculate repo-level splits (e.g. 80/10/10)
    # Guarantee >= 1 repo for val and test if we have at least 3 repos
    if num_repos >= 3:
        num_test = max(1, int(0.1 * num_repos))
        num_val = max(1, int(0.1 * num_repos))
        num_train = max(1, num_repos - num_val - num_test)
        
        train_cutoff = num_train
        val_cutoff = train_cutoff + num_val
    else:
        train_cutoff, val_cutoff = num_repos, num_repos
        
    for i, repo_path in enumerate(repo_paths):
        project_id = repo_path.name
        
        # Assign this repo to a split
        if i < train_cutoff:
            split_assignment = "train"
        elif i < val_cutoff:
            split_assignment = "val"
        else:
            split_assignment = "test"
            
        logging.info(f"Processing repository: {project_id} (Split: {split_assignment})")
        
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
            
            # Features (x) - Real CodeBERT embeddings
            embeddings = []
            with torch.no_grad():
                for node_id, node in graph.nodes.items():
                    # Extract semantic text. Use node name or metadata snippet
                    text_content = str(node.name) if hasattr(node, 'name') else str(node_id)
                    inputs = tokenizer(text_content, return_tensors="pt", truncation=True, max_length=512)
                    outputs = codebert_model(**inputs)
                    # Use the CLS token representation
                    cls_embedding = outputs.last_hidden_state[:, 0, :]
                    embeddings.append(cls_embedding.squeeze(0))
            
            x = torch.stack(embeddings)
            
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
            
            # Repository-level split: apply mask to ALL nodes in this repo
            train_mask = torch.zeros(num_nodes, dtype=torch.bool)
            val_mask = torch.zeros(num_nodes, dtype=torch.bool)
            test_mask = torch.zeros(num_nodes, dtype=torch.bool)
            
            if split_assignment == "train":
                train_mask[:] = True
            elif split_assignment == "val":
                val_mask[:] = True
            else:
                test_mask[:] = True
                
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
