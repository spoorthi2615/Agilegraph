from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict

class DatasetValidation(BaseModel):
    """
    Domain model representing the mathematical and structural integrity assessment 
    of a TrainingDataset prior to Graph Neural Network ingestion.
    """
    validation_id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    total_nodes: int
    total_edges: int
    feature_dimension: int
    
    label_distribution: Dict[str, int]
    isolated_nodes: int
    
    validation_passed: bool
    validation_messages: List[str]
