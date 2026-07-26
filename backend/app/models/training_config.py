from pydantic import BaseModel

class TrainingConfig(BaseModel):
    """
    Domain model encapsulating hyperparameters and configuration details 
    for executing a machine learning optimization loop.
    """
    optimizer_type: str = "Adam"
    learning_rate: float = 0.01
    weight_decay: float = 5e-4
    loss_function: str = "MSELoss"
    patience: int = 10
    checkpoint_path: str = "model_checkpoint.pt"
