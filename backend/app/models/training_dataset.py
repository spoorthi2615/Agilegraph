from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

class TrainingDataset(BaseModel):
    """
    Domain model representing a mathematically structured, machine-learning-ready 
    graph dataset extracted from an object-oriented CryptoGraph.
    """
    dataset_id: UUID = Field(default_factory=uuid4)
    project_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    total_nodes: int
    total_edges: int
    
    # 2D Array / List of Lists representing numerical features per node
    node_features: List[List[float]]
    
    # Topological mapping as a list of (source_index, target_index) tuples
    edge_index: List[Tuple[int, int]]
    
    # Ground truth labels for nodes (e.g. integer risk scores or classifications)
    node_labels: List[int]
    
    # Traceability payload (e.g., UUID-to-integer mappings)
    metadata: Dict[str, Any] = Field(default_factory=dict)
