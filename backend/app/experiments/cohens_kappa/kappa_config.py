from pydantic import BaseModel, Field

class KappaConfig(BaseModel):
    """
    Configuration for Cohen's Kappa agreement framework.
    """
    output_directory: str = Field(default="outputs/cohens_kappa")
