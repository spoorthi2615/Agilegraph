import torch
from pydantic import BaseModel, Field


class TrainingConfig(BaseModel):
    model_type: str = "GATv2"
    """
    Strongly typed configuration for the GATv2 training pipeline.
    Ensures reproducibility and eliminates hardcoded hyperparameters.
    """
    epochs: int = Field(default=100, ge=1)
    batch_size: int = Field(default=32, ge=1)
    learning_rate: float = Field(default=0.005, gt=0)
    weight_decay: float = Field(default=5e-4, ge=0)

    hidden_dim: int = Field(default=64, ge=1)
    out_dim: int = Field(default=2, ge=2)  # 2 classes: Safe (0), Vulnerable (1)
    heads: int = Field(default=8, ge=1)
    dropout: float = Field(default=0.6, ge=0, le=1)

    patience: int = Field(default=10, ge=1)
    min_delta: float = Field(default=0.001, ge=0)

    seed: int = Field(default=42)
    device: str = Field(default="cuda" if torch.cuda.is_available() else "cpu")
