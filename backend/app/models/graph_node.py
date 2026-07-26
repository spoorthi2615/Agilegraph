from typing import Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    """
    Data model representing a generic entity (node) within the cryptographic graph.
    """
    node_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the node")
    node_type: str = Field(..., description="The semantic classification of the node (e.g., 'Asset', 'File')")
    label: str = Field(..., description="A human-readable label or name for the node")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible key-value pairs for arbitrary node properties")
