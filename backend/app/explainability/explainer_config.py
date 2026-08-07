from pydantic import BaseModel, Field


class ExplainerConfig(BaseModel):
    """
    Hyper-parameters and configuration for PyTorch Geometric's GNNExplainer.
    """

    epochs: int = Field(default=200, description="Number of epochs to train the explainer mask.")
    lr: float = Field(default=0.01, description="Learning rate for the explainer optimizer.")
    threshold: float = Field(
        default=0.5, description="Threshold for determining important edges and features."
    )
    return_type: str = Field(
        default="log_prob", description="The return type of the GNN model (log_prob, prob, raw)."
    )
