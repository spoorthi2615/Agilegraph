from pydantic import BaseModel

class ComponentToggle(BaseModel):
    """
    Defines which architectural components of AgileGraph are currently active.
    Used during ablation studies to selectively disable features and measure their impact.
    """
    enable_graph_topology: bool = True
    enable_dependencies: bool = True
    enable_certificates: bool = True
    enable_risk_propagation: bool = True
    enable_deterministic_features: bool = True
    enable_attention_layer: bool = True
