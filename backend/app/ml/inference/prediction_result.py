from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.ml.inference.prediction import Prediction


class PredictionResult(BaseModel):
    """
    Container representing the complete set of predictions for a scanned repository.
    """

    project_id: str
    model_version: str
    inference_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    predictions: List[Prediction]
