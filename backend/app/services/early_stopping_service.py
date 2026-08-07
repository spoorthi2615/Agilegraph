import logging

logger = logging.getLogger(__name__)


class EarlyStoppingService:
    """
    Service responsible for convergence monitoring.
    Maintains a patience counter based on a target metric (e.g., validation loss).
    """

    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")
        self.early_stop = False

    def step(self, val_loss: float) -> bool:
        """
        Evaluates the new validation loss.
        Returns True if the metric improved, False otherwise.
        Updates self.early_stop if the patience counter is exceeded.
        """
        if val_loss < (self.best_loss - self.min_delta):
            self.best_loss = val_loss
            self.counter = 0
            return True
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                logger.info(
                    f"Early stopping triggered after {self.patience} epochs of no improvement."
                )
            return False
