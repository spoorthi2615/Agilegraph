from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class Expert(BaseModel):
    """
    Represents an independent human cybersecurity expert participating in the validation phase.
    """

    expert_id: str
    years_of_experience: int = Field(ge=0)
    area_of_expertise: str
    organization: Optional[str] = None
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
