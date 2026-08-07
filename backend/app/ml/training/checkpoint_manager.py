import logging
import os

import torch


class CheckpointManager:
    """
    Manages saving and restoring model and optimizer states.
    Ensures that the best weights are securely persisted for production inference.
    """

    def __init__(self, checkpoint_dir: str = "outputs/models"):
        self.checkpoint_dir = checkpoint_dir
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

    def save_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        val_loss: float,
        filename: str = "gatv2_best.pt",
    ):
        """
        Serializes the state dictionaries to disk.
        """
        path = os.path.join(self.checkpoint_dir, filename)

        # Extract architecture metadata directly from the model to persist it inside the checkpoint
        architecture = {
            "in_dim": model.conv1.in_channels,
            "hidden_dim": model.conv1.out_channels,
            "out_dim": model.conv2.out_channels,
            "heads": getattr(model.conv1, "heads", 1),
            "dropout": getattr(model.conv1, "dropout", getattr(model, "dropout", 0.0)),
        }

        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": val_loss,
                "architecture": architecture,
            },
            path,
        )
        logging.info(f"Checkpoint saved to {path} (Val Loss: {val_loss:.4f})")

    def load_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        filename: str = "gatv2_best.pt",
    ):
        """
        Deserializes the state dictionaries from disk and injects them into the model and optimizer.
        """
        path = os.path.join(self.checkpoint_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No checkpoint found at {path}")

        # load onto cpu first to avoid CUDA memory issues, then model handles moving it to correct device
        checkpoint = torch.load(path, map_location=torch.device("cpu"), weights_only=True)
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        logging.info(
            f"Checkpoint loaded from {path} (Epoch: {checkpoint['epoch']}, Val Loss: {checkpoint['val_loss']:.4f})"
        )
        return checkpoint["epoch"], checkpoint["val_loss"]
