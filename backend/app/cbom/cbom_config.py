from typing import List

from pydantic import BaseModel, Field


class CBOMConfig(BaseModel):
    """
    Configuration properties for the CBOM Parsing and Validation engine.
    """

    supported_formats: List[str] = Field(default=["cyclonedx-cbom", "agilegraph-cbom-v1"])
    strict_validation: bool = Field(default=True)
    require_asset_identifiers: bool = Field(default=True)
