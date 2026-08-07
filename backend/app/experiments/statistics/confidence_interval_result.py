from typing import Dict

from pydantic import BaseModel

from app.experiments.statistics.confidence_interval import ConfidenceInterval


class ConfidenceIntervalResult(BaseModel):
    """
    Container for all computed metric confidence intervals for a specific experiment track.
    """

    experiment_name: str
    metrics: Dict[str, ConfidenceInterval]
