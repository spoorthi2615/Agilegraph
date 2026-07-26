from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Any
from datetime import datetime, timezone

class ExplanationResult(BaseModel):
    """
    Strongly typed payload containing the explanation for a specific neural network prediction.
    """
    project_id: str
    node_id: int
    predicted_class: int
    prediction_probability: float
    
    important_nodes: List[int] = Field(default_factory=list)
    important_edges: List[Tuple[int, int]] = Field(default_factory=list)
    important_features: List[int] = Field(default_factory=list)
    
    feature_scores: Dict[str, float] = Field(default_factory=dict)
    node_scores: Dict[str, float] = Field(default_factory=dict)
    edge_scores: Dict[str, float] = Field(default_factory=dict)
    
    generation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_graph_edges(self) -> List[Tuple[str, str, str]]:
        """
        Translates the explanation into graph edges for database injection.
        """
        edges = []
        explanation_node = f"Explanation:{self.node_id}_{self.generation_timestamp[:10]}"
        target_node = f"CryptoNode:{self.node_id}"
        
        edges.append((explanation_node, "EXPLAINS", target_node))
        
        for feat in self.important_features:
            edges.append((explanation_node, "IDENTIFIES_IMPORTANT_FEATURE", f"Feature:{feat}"))
            
        for edge_tuple in self.important_edges:
            edge_id = f"{edge_tuple[0]}_{edge_tuple[1]}"
            edges.append((explanation_node, "IDENTIFIES_IMPORTANT_EDGE", f"GraphEdge:{edge_id}"))
            
        return edges
