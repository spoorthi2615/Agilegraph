import copy
import logging

import torch


class EarlyStopping:
    """
    Halts training when validation loss stops improving to prevent overfitting.
    Automatically caches the best model weights observed during training.
    """

    def __init__(self, patience: int = 10, min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        self.best_weights = None

    def __call__(self, val_loss: float, model: torch.nn.Module):
        """
        Evaluate current validation loss against the best observed loss.
        """
        if self.best_loss is None:
            self.best_loss = val_loss
            self.best_weights = copy.deepcopy(model.state_dict())
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                logging.info(
                    f"Early stopping triggered after {self.counter} epochs without improvement."
                )
        else:
            self.best_loss = val_loss
            self.best_weights = copy.deepcopy(model.state_dict())
            self.counter = 0

    def restore_best_weights(self, model: torch.nn.Module):
        """
        Injects the cached best weights back into the model.
        """
        if self.best_weights is not None:
            model.load_state_dict(self.best_weights)
            logging.info("Restored best model weights from EarlyStopping cache.")
