from pydantic import BaseModel, Field

class FleissConfig(BaseModel):
    """
    Configuration for Fleiss' Kappa multi-rater agreement framework.
    """
    output_directory: str = Field(default="outputs/fleiss_kappa")
