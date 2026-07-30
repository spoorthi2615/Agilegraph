from typing import Any
import time
import logging
from datetime import datetime, timezone

from app.models.inference_result import InferenceResult, NodePrediction
from app.models.inference_dataset import InferenceDataset
from app.models.model_config import ModelConfig

logger = logging.getLogger(__name__)

import torch
import torch.nn as nn


class GATv2InferenceService:
    """
    Service responsible for explicitly generating real-time predictions using a trained GATv2 model 
    on new, unseen data, and mapping those predictions securely back to their source UUIDs.
    """

    @classmethod
    def run_inference(
        cls,
        model: Any,
        dataset: InferenceDataset,
        config: ModelConfig
    ) -> InferenceResult:
        """
        Executes a highly optimized, deterministic forward pass over the dataset with gradients disabled.
        Generates continuous risk scores and discrete labels mapped to exact graph nodes.
        """
        start_time = time.perf_counter()
        
        # 1. Read the classification threshold from ModelConfig (with safe fallback)
        # Allows dynamic thresholding without hardcoding logic.
        if hasattr(config, "classification_threshold"):
            threshold = getattr(config, "classification_threshold")
        elif hasattr(config, "model_extra") and config.model_extra and "classification_threshold" in config.model_extra:
            threshold = config.model_extra["classification_threshold"]
        else:
            threshold = 75.0
            
        threshold = float(threshold)
        
        # 2. Verify Model Compatibility
        if not isinstance(model, nn.Module):
            raise TypeError("Provided model instance is not a valid PyTorch nn.Module. Cannot run inference.")
            
        # 3. Setup Inference Tensors
        x_tensor = torch.tensor(dataset.node_features, dtype=torch.float)
        
        if not dataset.edge_index:
            raise ValueError("Inference Dataset contains no topological edges. Message passing is impossible.")
            
        src_list = [edge[0] for edge in dataset.edge_index]
        tgt_list = [edge[1] for edge in dataset.edge_index]
        edge_index_tensor = torch.tensor([src_list, tgt_list], dtype=torch.long)
        
        # 4. Switch Model to Evaluation Mode (Disables Dropout layers)
        model.eval()
        
        # 5. Disable Gradients (Crucial for memory efficiency during production inference)
        with torch.no_grad():
            
            # 6. Execute Forward Pass
            out = model(x_tensor, edge_index_tensor)
            
            # 7. Generate Predicted Risk Scores
            probs = torch.sigmoid(out)
            scaled_scores = probs * 100.0
            
            # 8. Generate Discrete Labels using the classification threshold
            preds = (scaled_scores >= threshold).int()
            
        # Convert GPU/CPU tensors cleanly back to native Python lists
        predicted_risk_scores = scaled_scores.cpu().numpy().flatten().tolist()
        predicted_labels = preds.cpu().numpy().flatten().tolist()
        
        # 9. Map Predictions Back to Original Nodes
        # Extract the node UUID to Index mapping generated during dataset extraction
        node_index_mapping = dataset.metadata.get("node_index_mapping", {})
        
        # Invert the dictionary to map Index -> UUID String
        index_to_uuid = {int(idx): uid_str for uid_str, idx in node_index_mapping.items()}
        
        node_predictions = []
        for i in range(len(predicted_risk_scores)):
            # Lookup the original node UUID, fallback to placeholder if somehow missing
            uid_str = index_to_uuid.get(i, f"unknown-node-{i}")
            
            node_predictions.append(
                NodePrediction(
                    node_id=uid_str,
                    risk_score=float(predicted_risk_scores[i]),
                    label=int(predicted_labels[i])
                )
            )
        
        # 10. Measure Inference Duration
        end_time = time.perf_counter()
        completed_at = datetime.now(timezone.utc)
        duration = end_time - start_time
        
        # 11. Return fully traceable InferenceResult
        return InferenceResult(
            model_id=config.model_id,
            dataset_id=dataset.dataset_id,
            inferred_at=completed_at,
            total_predictions=len(node_predictions),
            node_predictions=node_predictions,
            classification_threshold=threshold,
            inference_duration_seconds=duration,
            inference_completed=True,
            metadata={"device": "cpu"}
        )
