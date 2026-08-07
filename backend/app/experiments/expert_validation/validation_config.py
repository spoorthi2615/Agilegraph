from pydantic import BaseModel, Field


class ValidationConfig(BaseModel):
    """
    Configuration mapping for tie-breaking and consensus logic.
    """

    tie_breaker_strategy: str = Field(
        default="highest_risk", description="Strategy for breaking ties: 'highest_risk', 'unknown'"
    )
    drop_unknowns_if_possible: bool = Field(
        default=True,
        description="If True, UNKNOWN labels are ignored during majority voting unless all labels are UNKNOWN.",
    )
    output_directory: str = Field(default="outputs/expert_validation")
