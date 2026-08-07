import logging
import os
from typing import Optional

import torch
import torch.nn.functional as F

from app.ml.datasets.graph_dataset import GraphDatasetWrapper
from app.ml.inference.inference_config import InferenceConfig
from app.ml.inference.model_loader import ModelLoader
from app.ml.inference.prediction import Prediction
from app.ml.inference.prediction_result import PredictionResult
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset


class InferenceService:
    """
    Production service orchestrating the GATv2 inference pipeline.
    Maintains model state in memory for fast, batched evaluation of new repositories.
    """

    def __init__(self, config: Optional[InferenceConfig] = None):
        self.config = config or InferenceConfig()
        self.device = torch.device(self.config.device)
        self.model = None  # Lazy loaded on first request to capture dynamic in_dim

    def predict(self, dataset: TrainingDataset, graph: CryptoGraph) -> PredictionResult:
        """
        Executes a complete forward pass and returns structured PredictionResult.
        """
        model_version = os.path.basename(self.config.checkpoint_path)

        if not dataset.node_features:
            logging.warning(
                f"Empty dataset provided for project {dataset.project_id}. Returning empty result."
            )
            return PredictionResult(
                project_id=dataset.project_id, model_version=model_version, predictions=[]
            )

        # Compile PyG Data Tensor and move to device
        pyg_data = GraphDatasetWrapper.to_pyg_data(dataset).to(self.device)

        # Lazy load model if not initialized or if in_dim changed
        in_dim = pyg_data.x.shape[1]
        if self.model is None or self.model.conv1.in_channels != in_dim:
            logging.info(f"Initializing model for input dimension {in_dim}")
            self.model = ModelLoader.load(self.config, in_dim=in_dim)

        # Execute pure inference securely without gradient tracking
        with torch.no_grad():
            logits = self.model(pyg_data)
            probs = F.softmax(logits, dim=1)
            preds = logits.argmax(dim=1)

        # Map predictions back to the original domain graph nodes
        sorted_nodes = sorted(graph.nodes.values(), key=lambda n: str(n.node_id))

        predictions = []
        for idx, node in enumerate(sorted_nodes):
            predictions.append(
                Prediction(
                    node_id=node.node_id,
                    predicted_class=preds[idx].item(),
                    confidence_score=probs[idx][preds[idx]].item(),
                    probabilities=probs[idx].tolist(),
                )
            )

        return PredictionResult(
            project_id=dataset.project_id, model_version=model_version, predictions=predictions
        )
