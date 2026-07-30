from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Dict, Any

class TrainingResult(BaseModel):
    """
    Domain model representing the comprehensive metrics, telemetry, and final outcome 
    of a Graph Neural Network training session.
    """
    training_id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    dataset_id: UUID
    
    started_at: datetime
    completed_at: datetime
    
    epochs: int
    learning_rate: float
    optimizer: str
    
    loss_history: List[float]
    final_training_loss: float
    training_duration_seconds: float
    
    training_completed: bool
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
