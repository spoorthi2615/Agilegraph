from typing import List

from pydantic import BaseModel, Field


class DetectedLanguage(BaseModel):
    """
    Data model representing a programming language detected within a project repository.
    """

    language: str = Field(
        ..., description="The name of the detected programming language (e.g., 'Python', 'Java')"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score of the detection ranging from 0.0 to 1.0"
    )
    indicators: List[str] = Field(
        ..., description="A list of specific file names or extensions that triggered this detection"
    )
