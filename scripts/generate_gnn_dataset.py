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
    
    repo_paths = sorted([p for p in corpus_dir.iterdir() if p.is_dir()])
    
    # Repo level split assignments are removed. K-Fold cross-validation will be handled dynamically in run_experiments.py
    for i, repo_path in enumerate(repo_paths):
        project_id = repo_path.name
        logging.info(f"Processing repository: {project_id}")
        
        try:
            # 1. Static Analysis
            analysis_result = analysis_service.analyze_project(project_id, repo_path)
            
            # Sort the findings deterministically to ensure GraphBuilder insertion order is stable
            analysis_result.scanner_results.sort(key=lambda sr: str(sr.scanner_name))
            for scanner_result in analysis_result.scanner_results:
                scanner_result.findings.sort(key=lambda f: (
                    str(f.get('file_path', '')),
                    str(f.get('line_number', '')),
                    str(f.get('algorithm', '')),
                    str(f.get('asset_type', ''))
                ))
            
            # 2. Scoring
            for scanner_result in analysis_result.scanner_results:
                assets = [CryptoAsset(**finding) for finding in scanner_result.findings]
                scored_assets = RiskScoringService.score_assets(assets)
                scanner_result.findings = [asset.model_dump(mode="json") for asset in scored_assets]
                
            # 3. Dependency Mapping
            raw_dependency_map = DependencyMappingService.map_dependencies(repo_path)
            
            # Sort the dependency map deterministically
            dependency_map = {
                k: sorted(v) for k, v in sorted(raw_dependency_map.items())
            }
            
            # 4. Graph Building
            graph = GraphBuilder.build_graph(analysis_result, dependency_map)
            logging.info(f"Built graph for {project_id}: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            # 5. Convert to PyTorch Geometric Data

            num_nodes = len(graph.nodes)
            if num_nodes == 0:
                logging.warning(f"No nodes found for {project_id}, skipping.")
                continue
                
            # Map node IDs to integers deterministically (UUIDs are random, so we must sort by node properties!)
            def node_sort_key(node_id):
                n = graph.nodes[node_id]
                return (
                    str(getattr(n, 'node_type', '')),
                    str(getattr(n, 'label', '')),
                    str(getattr(n, 'metadata', {}).get('file_path', '')),
                    str(getattr(n, 'metadata', {}).get('line_number', ''))
                )
                
            sorted_node_ids = sorted(graph.nodes.keys(), key=node_sort_key)
            node_mapping = {node_id: idx for idx, node_id in enumerate(sorted_node_ids)}
            
            # Features (x) - Real CodeBERT embeddings + base_risk scalar
            embeddings = []
            with torch.no_grad():
                for node_id in sorted_node_ids:
                    node = graph.nodes[node_id]
                    # Extract semantic text
                    text_content = str(node.label) if hasattr(node, 'label') else "unknown"
                    inputs = tokenizer(text_content, return_tensors="pt", truncation=True, max_length=512)
                    outputs = codebert_model(**inputs)
                    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze(0)
                    
                    # Extract heuristic base risk (P2.1)
                    meta = getattr(node, 'metadata', {})
                    if not isinstance(meta, dict):
                        meta = {}
                    risk_score = float(meta.get("risk_score", 0.0))
                    
                    # Concatenate (768 + 1 = 769 dimensions)
                    emb_with_risk = torch.cat([cls_embedding, torch.tensor([risk_score])], dim=-1)
                    embeddings.append(emb_with_risk)
            
            x = torch.stack(embeddings)
            
            # Feature Standardization: Zero-Mean, Unit-Variance per feature dimension
            if x.shape[0] > 1:
                x_mean = x.mean(dim=0, keepdim=True)
                x_std = x.std(dim=0, keepdim=True)
                x_std[x_std == 0] = 1.0  # Prevent division by zero
                x = (x - x_mean) / x_std
            
            # Edges (edge_index)
            edge_index = []
            edge_attr = []
            
            # Sort edges by source and target properties to ensure deterministic message passing order
            def edge_sort_key(e):
                return (
                    node_sort_key(e.source_node),
                    node_sort_key(e.target_node),
                    str(getattr(e, 'edge_type', ''))
                )
                
            sorted_edges = sorted(graph.edges, key=edge_sort_key)
            
            for edge in sorted_edges:
                src = node_mapping.get(edge.source_node)
                dst = node_mapping.get(edge.target_node)
                if src is not None and dst is not None:
                    edge_index.append([src, dst])
                    # One-hot encode edge_type
                    etype = getattr(edge, 'edge_type', '')
                    if etype == "CONTAINS":
                        edge_attr.append([1.0, 0.0, 0.0])
                    elif etype == "USES":
                        edge_attr.append([0.0, 1.0, 0.0])
                    else:
                        edge_attr.append([0.0, 0.0, 1.0])
                    
            if not edge_index:
                edge_index = torch.empty((2, 0), dtype=torch.long)
                edge_attr = torch.empty((0, 3), dtype=torch.float)
            else:
                edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
                edge_attr = torch.tensor(edge_attr, dtype=torch.float)
                
            # Labels (y) - Deterministic labels derived from crypto primitives
            # 1: Vulnerable/Legacy (RSA, ECDSA, DSA, 3DES, MD5, SHA1)
            # 0: Safe/Neutral (ML-KEM, ML-DSA, SLH-DSA, or no crypto found)
            y = torch.zeros(num_nodes, dtype=torch.long)
            vulnerable_primitives = ["rsa", "ecdsa", "dsa", "des", "3des", "md5", "sha1"]
            
            node_names_list = []
            for idx, node_id in enumerate(sorted_node_ids):
                node = graph.nodes[node_id]
                # Extract text context to search for primitives
                raw_node_name = str(node.label) if hasattr(node, 'label') else "unknown"
                node_name = f"{repo_path.name}::{raw_node_name}"
                node_names_list.append(node_name)
                
                node_text = (raw_node_name + " " + str(node.metadata)).lower()
                is_vulnerable = any(prim in node_text for prim in vulnerable_primitives)
                if is_vulnerable:
                    y[idx] = 1
                    
            data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr, y=y, node_names=node_names_list, repo_name=project_id)
            
            # Save tensor (Masks are removed, run_experiments.py will handle train/val/test dynamically)
            
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
