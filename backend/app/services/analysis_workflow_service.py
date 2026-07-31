from pathlib import Path
from typing import Dict, Any

from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.graph.graph_builder import GraphBuilder
from app.services.neo4j_export_service import Neo4jExportService
from app.models.crypto_asset import CryptoAsset

class AnalysisWorkflowService:
    """
    Facade service orchestrating the entire static analysis pipeline.
    Encapsulates all domain transformations and state mutations so that
    presentation layers (like REST routers) remain strictly decoupled.
    """
    from app.services.scan_status_service import ScanStatusService, ScanStage
    def __init__(
        self,
        analysis_service: ProjectAnalysisService,
        export_service: Neo4jExportService
    ) -> None:
        self.analysis_service = analysis_service
        self.export_service = export_service

    def execute_pipeline(self, project_id: str, project_path: Path) -> Dict[str, Any]:
        """
        Sequentially executes the scan, score, graph build, and export workflow.
        Returns a simplified statistics summary object.
        """
        try:
            from app.services.scan_status_service import ScanStatusService, ScanStage
            
            # Step 1: Execute static analysis scanners
            ScanStatusService.set_status(project_id, ScanStage.SCANNING)
            analysis_result = self.analysis_service.analyze_project(project_id, project_path)
            
            # Step 2: Apply risk scoring rules via internal hydration/dehydration
            ScanStatusService.set_status(project_id, ScanStage.SCORING)
            for scanner_result in analysis_result.scanner_results:
                assets = [CryptoAsset(**finding) for finding in scanner_result.findings]
                scored_assets = RiskScoringService.score_assets(assets)
                scanner_result.findings = [asset.model_dump(mode="json") for asset in scored_assets]
                
            # Step 2.5: Map internal dependencies
            from app.services.dependency_mapping_service import DependencyMappingService
            dependency_map = DependencyMappingService.map_dependencies(project_path)
            
            # Step 3: Transform into Graph Domain Model
            ScanStatusService.set_status(project_id, ScanStage.BUILDING_GRAPH)
            graph = GraphBuilder.build_graph(analysis_result, dependency_map)
            
            # Step 3.5: Run ML Inference to override heuristic risk scores
            # Only runs if CodeBERT is already cached locally — skips gracefully on Vercel/cold start
            try:
                import torch
                from transformers import AutoTokenizer, AutoModel
                from app.models.inference_dataset import InferenceDataset
                from app.ml.inference.inference_config import InferenceConfig
                from app.ml.inference.model_loader import ModelLoader
                from app.services.gatv2_inference_service import GATv2InferenceService
                import logging

                # Check if model is cached before trying to load it (avoids hanging download)
                from pathlib import Path as _Path
                import os as _os
                _hf_cache = _os.environ.get("HF_HOME", _os.path.expanduser("~/.cache/huggingface"))
                _model_cached = (_Path(_hf_cache) / "hub" / "models--microsoft--codebert-base").exists()

                if not _model_cached:
                    logging.info(f"[{project_id}] CodeBERT not cached locally — skipping ML inference, using heuristic scores.")
                    raise RuntimeError("CodeBERT not cached; skipping ML step.")
                
                logging.info(f"[{project_id}] Building InferenceDataset via CodeBERT...")
                
                node_mapping = {node_id: idx for idx, node_id in enumerate(graph.nodes.keys())}
                index_to_uuid = {idx: node_id for node_id, idx in node_mapping.items()}
                
                tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base", local_files_only=True)
                codebert_model = AutoModel.from_pretrained("microsoft/codebert-base", local_files_only=True)
                codebert_model.eval()

                embeddings = []
                with torch.no_grad():
                    for node_id, node in graph.nodes.items():
                        text_content = str(node.name) if hasattr(node, 'name') else str(node_id)
                        inputs = tokenizer(text_content, return_tensors="pt", truncation=True, max_length=512)
                        outputs = codebert_model(**inputs)
                        cls_embedding = outputs.last_hidden_state[:, 0, :]
                        embeddings.append(cls_embedding.squeeze(0).tolist())
                
                edge_index = []
                for edge in graph.edges:
                    src = node_mapping.get(edge.source_node)
                    dst = node_mapping.get(edge.target_node)
                    if src is not None and dst is not None:
                        edge_index.append((src, dst))
                        
                inf_dataset = InferenceDataset(
                    project_id=project_id,
                    total_nodes=len(graph.nodes),
                    total_edges=len(edge_index),
                    node_features=embeddings,
                    edge_index=edge_index,
                    metadata={"node_index_mapping": index_to_uuid}
                )

                logging.info(f"[{project_id}] Running GATv2 Inference...")
                inf_config = InferenceConfig(checkpoint_path="backend/data/models/gatv2_best.pt")
                loaded_model = ModelLoader.load(inf_config, in_dim=768)
                
                inf_result = GATv2InferenceService.run_inference(loaded_model, inf_dataset, inf_config)
                
                # Apply ML predictions back to the Graph Nodes
                for pred in inf_result.node_predictions:
                    node = graph.nodes.get(pred.node_id)
                    if node:
                        node.metadata["risk_score"] = pred.risk_score
                        node.metadata["severity"] = "CRITICAL" if pred.label == 1 else "LOW"
                logging.info(f"[{project_id}] Successfully overrode graph with ML predictions.")
            except Exception as ml_err:
                import logging
                logging.warning(f"[{project_id}] ML Inference skipped (using heuristic scores): {ml_err}")
            
            # Step 4: Export to physical Neo4j cluster (best-effort — scan completes even if Neo4j is down)
            ScanStatusService.set_status(project_id, ScanStage.EXPORTING)
            try:
                self.export_service.export_graph(graph)
            except Exception as neo4j_err:
                import logging
                logging.warning(f"[{project_id}] Neo4j export failed (scan still marked complete): {neo4j_err}")
            
            ScanStatusService.set_status(project_id, ScanStage.COMPLETED)
            
            # Return standardized metrics
            return {
                "status": "success",
                "total_findings": analysis_result.total_findings,
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges)
            }
            
        except Exception as e:
            from app.services.scan_status_service import ScanStatusService, ScanStage
            ScanStatusService.set_status(project_id, ScanStage.FAILED)
            raise e
        finally:
            self.export_service.close()
