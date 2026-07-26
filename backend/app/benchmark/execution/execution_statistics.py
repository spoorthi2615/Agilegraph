from pydantic import BaseModel
from typing import Dict

class MetricStats(BaseModel):
    average: float
    std_dev: float
    min_val: float
    max_val: float

class BaselineStatistics(BaseModel):
    """
    Aggregated statistical distribution for a single baseline across all tested repositories.
    """
    baseline_name: str
    total_repositories_tested: int
    
    accuracy: MetricStats
    macro_precision: MetricStats
    macro_recall: MetricStats
    macro_f1: MetricStats
    
    weighted_precision: MetricStats
    weighted_recall: MetricStats
    weighted_f1: MetricStats
    
    execution_time_ms: MetricStats

class ExperimentStatistics(BaseModel):
    """
    Final output document containing comparative aggregate metrics for all baselines.
    """
    baselines: Dict[str, BaselineStatistics]
