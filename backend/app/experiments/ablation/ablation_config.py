from typing import List
from pydantic import BaseModel, Field
from app.experiments.ablation.component_toggle import ComponentToggle

class AblationExperiment(BaseModel):
    name: str
    toggle: ComponentToggle

class AblationConfig(BaseModel):
    experiments: List[AblationExperiment] = Field(default_factory=list)
    dataset_ids: List[str] = Field(default_factory=list)
    output_directory: str = "outputs/ablation"
    
    @classmethod
    def default_matrix(cls) -> "AblationConfig":
        return cls(
            experiments=[
                AblationExperiment(name="Full Model", toggle=ComponentToggle()),
                AblationExperiment(name="Without Graph Features", toggle=ComponentToggle(enable_graph_topology=False)),
                AblationExperiment(name="Without Dependency Features", toggle=ComponentToggle(enable_dependencies=False)),
                AblationExperiment(name="Without Certificate Features", toggle=ComponentToggle(enable_certificates=False)),
                AblationExperiment(name="Without Risk Propagation", toggle=ComponentToggle(enable_risk_propagation=False)),
                AblationExperiment(name="Without Deterministic Risk Features", toggle=ComponentToggle(enable_deterministic_features=False)),
                AblationExperiment(name="Without Attention Layer", toggle=ComponentToggle(enable_attention_layer=False)),
            ]
        )
