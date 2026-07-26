from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime, timezone

class CBOMAsset(BaseModel):
    """
    Strongly typed representation of a Cryptographic Asset derived from a CBOM document.
    """
    asset_id: str
    algorithm: str
    library: Optional[str] = None
    version: Optional[str] = None
    key_size: Optional[int] = None
    certificate: Optional[str] = None
    provider: Optional[str] = None
    application: Optional[str] = None
    dependency: Optional[str] = None

class CBOMInventory(BaseModel):
    """
    A collection of CBOM Assets representing an external cryptographic baseline.
    """
    document_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    assets: List[CBOMAsset] = Field(default_factory=list)

class CBOMComparison(BaseModel):
    """
    The output of the Comparator engine. Represents the bidirectional diff.
    """
    matched_assets: List[CBOMAsset] = Field(default_factory=list)
    missing_assets: List[CBOMAsset] = Field(default_factory=list)      # In AgileGraph but not in CBOM
    unexpected_assets: List[CBOMAsset] = Field(default_factory=list)   # In CBOM but not discovered in AgileGraph
    mismatched_assets: List[Dict[str, Any]] = Field(default_factory=list) # Found in both, but fields differ
    
    summary: Dict[str, int] = Field(default_factory=dict)
    
    def to_graph_edges(self, cbom_document_id: str) -> List[Tuple[str, str, str]]:
        """
        Translates the comparison state into Graph Database edges.
        Format: (SourceNode, RELATIONSHIP, TargetNode)
        """
        edges = []
        doc_node = f"CBOM:{cbom_document_id}"
        
        for asset in self.matched_assets:
            asset_node = f"CryptoAsset:{asset.asset_id}"
            edges.append((doc_node, "VERIFIES", asset_node))
            
        for asset in self.unexpected_assets:
            asset_node = f"CryptoAsset:{asset.asset_id}"
            edges.append((doc_node, "CLAIMS_PRESENCE_OF", asset_node))
            if asset.application:
                edges.append((asset_node, "BELONGS_TO", f"Application:{asset.application}"))
            if asset.dependency:
                edges.append((asset_node, "BELONGS_TO", f"Dependency:{asset.dependency}"))
                
        return edges
