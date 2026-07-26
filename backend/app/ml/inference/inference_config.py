import torch
from pydantic import BaseModel, Field

class InferenceConfig(BaseModel):
    """
    Configuration model for the GATv2 Inference Pipeline.
    Defines structural model parameters necessary for instantiation and target device logic.
    """
    # Architecture params (must align with the trained checkpoint)
    hidden_dim: int = Field(default=64, ge=1)
    out_dim: int = Field(default=4, ge=2)
    heads: int = Field(default=8, ge=1)
    dropout: float = Field(default=0.0) # Dropout is disabled during inference via .eval() anyway
    
    # Checkpoint details
    checkpoint_path: str = Field(default="outputs/models/gatv2_best.pt")
    
    # Execution details
    device: str = Field(default="cuda" if torch.cuda.is_available() else "cpu")
