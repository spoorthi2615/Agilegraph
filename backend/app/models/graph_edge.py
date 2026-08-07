from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GraphEdge(BaseModel):
    """
    Data model representing a directional relationship (edge) between two nodes in the cryptographic graph.
    """

    edge_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the edge itself"
    )
    source_node: UUID = Field(..., description="The UUID of the origin node")
    target_node: UUID = Field(..., description="The UUID of the destination node")
    edge_type: str = Field(
        ..., description="The semantic relationship type (e.g., 'CALLS', 'CONTAINS', 'IMPLEMENTS')"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Flexible key-value pairs for arbitrary edge properties"
    )
