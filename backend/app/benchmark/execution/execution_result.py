from pydantic import BaseModel
from typing import List

class ExecutionResult(BaseModel):
    """
    Repository-level benchmark mathematical metrics for a specific baseline.
    Produced by comparing the Baseline predictions against ground-truth labels.
    """
    project_id: str
    baseline_name: str
    
    # Standard Classification
    accuracy: float
    
    # Macro Average
    macro_precision: float
    macro_recall: float
    macro_f1: float
    
    # Weighted Average
    weighted_precision: float
    weighted_recall: float
    weighted_f1: float
    
    # Raw stats
    execution_time_ms: float
    prediction_count: int
    support: int
    
    # 4x4 Confusion Matrix (nested lists for JSON serialization)
    confusion_matrix: List[List[int]]
