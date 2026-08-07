from typing import List

from pydantic import BaseModel, Field


class BenchmarkConfig(BaseModel):
    """
    Configuration parameters for the Baseline Benchmark Framework.
    """

    enabled_baselines: List[str] = Field(default=["rule_based", "graph_centrality", "random"])
    execution_timeout_seconds: int = Field(default=300)
    parallel_execution: bool = Field(default=False)
    output_directory: str = Field(default="backend/outputs/benchmark")
