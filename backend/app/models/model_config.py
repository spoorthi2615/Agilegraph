from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """
    Configuration payload defining the mathematical hyperparameters and
    architectural dimensions for a Graph Neural Network.
    """

    model_id: UUID = Field(default_factory=uuid4)
    model_name: str = Field(default="GATv2", description="The architectural class of the model")
    input_dimension: int = Field(..., description="The exact feature length of the input nodes")
    hidden_dimension: int = Field(
        default=64, description="Dimensionality of hidden tensor representations"
    )
    output_dimension: int = Field(
        default=1,
        description="Dimensionality of the final prediction (e.g., 1 for regression/binary)",
    )
    attention_heads: int = Field(
        default=4, description="Number of parallel multi-head attention mechanisms"
    )
    num_layers: int = Field(default=2, description="Number of message passing layers")
    dropout: float = Field(default=0.2, description="Dropout probability for regularization")
    activation: str = Field(default="ELU", description="Non-linear activation function to apply")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
