import logging
from typing import Any
import os

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

class ModelCheckpointService:
    """
    Service exclusively responsible for persisting and loading PyTorch model weights.
    """
    
    @staticmethod
    def save_checkpoint(model: Any, filepath: str) -> None:
        """Saves the model state_dict to disk."""
        if not TORCH_AVAILABLE:
            return
        try:
            torch.save(model.state_dict(), filepath)
        except Exception as e:
            logger.error(f"Failed to save model checkpoint to {filepath}: {e}")

    @staticmethod
    def load_checkpoint(model: Any, filepath: str) -> None:
        """Loads the model state_dict from disk if it exists."""
        if not TORCH_AVAILABLE or not os.path.exists(filepath):
            return
        try:
            model.load_state_dict(torch.load(filepath))
            model.eval()
        except Exception as e:
            logger.error(f"Failed to load model checkpoint from {filepath}: {e}")
