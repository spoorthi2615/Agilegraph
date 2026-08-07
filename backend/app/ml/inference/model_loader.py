import logging
import os

import torch

from app.ml.inference.inference_config import InferenceConfig
from app.ml.models.gatv2_model import GATv2Model


class ModelLoader:
    """
    Reusable loader for the GATv2 model.
    Handles device placement, state deserialization, and dynamic input dimension inference.
    """

    @staticmethod
    def load(config: InferenceConfig, in_dim: int) -> GATv2Model:
        device = torch.device(config.device)
        if not os.path.exists(config.checkpoint_path):
            logging.warning(
                f"Checkpoint not found at {config.checkpoint_path}. Initializing an untrained GATv2Model for fallback inference."
            )
            model = GATv2Model(
                in_dim=in_dim,
                hidden_dim=config.hidden_dim,
                out_dim=config.out_dim,
                heads=config.heads,
                dropout=config.dropout,
            ).to(device)
            model.eval()
            return model

        device = torch.device(config.device)

        try:
            # Securely load weights (must allow dict loading for architecture metadata if present)
            checkpoint = torch.load(config.checkpoint_path, map_location=device, weights_only=True)

            # Prefer architecture stored in checkpoint, fallback to InferenceConfig
            arch = checkpoint.get("architecture", {})
            actual_hidden_dim = arch.get("hidden_dim", config.hidden_dim)
            actual_out_dim = arch.get("out_dim", config.out_dim)
            actual_heads = arch.get("heads", config.heads)

            # If checkpoint has explicit in_dim, use it (otherwise trust the incoming tensor size)
            actual_in_dim = arch.get("in_dim", in_dim)

            if not arch:
                logging.warning(
                    "Checkpoint missing architecture metadata. Falling back to InferenceConfig defaults, which may cause dimension mismatch."
                )

            # Initialize architecture dynamically
            model = GATv2Model(
                in_dim=actual_in_dim,
                hidden_dim=actual_hidden_dim,
                out_dim=actual_out_dim,
                heads=actual_heads,
                dropout=config.dropout,
            ).to(device)

            # Extract state dict
            state_dict = checkpoint.get("model_state_dict", checkpoint)

            model.load_state_dict(state_dict)

            # STRICT: Force evaluation mode to disable dropouts/batchnorm
            model.eval()

            logging.info(
                f"Successfully loaded GATv2 model from {config.checkpoint_path} onto {config.device}"
            )
            return model
        except Exception as e:
            logging.error(
                f"Failed to restore model weights from {config.checkpoint_path}: {str(e)}"
            )
            raise RuntimeError(f"Model restoration failed: {str(e)}")
