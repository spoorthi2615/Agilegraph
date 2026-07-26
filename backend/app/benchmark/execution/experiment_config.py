from pydantic import BaseModel, Field
from typing import List, Optional

class ExperimentConfig(BaseModel):
    """
    Configuration for executing large-scale benchmark experiments across datasets.
    """
    dataset_ids: Optional[List[str]] = None  # None implies execution on all available datasets
    enabled_baselines: List[str] = Field(default=["rule_based", "graph_centrality", "random"])
    batch_size: int = Field(default=1)
    random_seed: int = Field(default=42)
    output_directory: str = Field(default="outputs/experiments")
    parallel_execution: bool = Field(default=False)
