from pydantic import BaseModel, Field
from typing import List

class CBOMConfig(BaseModel):
    """
    Configuration properties for the CBOM Parsing and Validation engine.
    """
    supported_formats: List[str] = Field(default=["cyclonedx-cbom", "agilegraph-cbom-v1"])
    strict_validation: bool = Field(default=True)
    require_asset_identifiers: bool = Field(default=True)
