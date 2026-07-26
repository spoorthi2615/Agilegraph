from pydantic import BaseModel, Field

class WorkflowConfig(BaseModel):
    """
    Configuration for the master experiment workflow orchestrator.
    """
    output_directory: str = Field(default="outputs/workflow")
    run_benchmarks: bool = Field(default=True)
    run_ablation: bool = Field(default=True)
    run_bootstrap: bool = Field(default=True)
    run_significance: bool = Field(default=True)
    run_expert_validation: bool = Field(default=True)
