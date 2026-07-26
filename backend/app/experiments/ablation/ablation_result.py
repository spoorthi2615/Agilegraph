from pydantic import BaseModel

class AblationResult(BaseModel):
    experiment_name: str
    
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    
    weighted_precision: float
    weighted_recall: float
    weighted_f1: float
    
    execution_time_ms: float
    
    # Delta from Full Model
    accuracy_drop: float = 0.0
    macro_f1_drop: float = 0.0
    weighted_f1_drop: float = 0.0
    percentage_performance_drop: float = 0.0
