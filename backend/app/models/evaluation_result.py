from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """
    Domain model representing the empirical testing metrics and performance
    of a trained Graph Neural Network on an unseen evaluation dataset.
    """

    evaluation_id: UUID = Field(default_factory=uuid4)
    training_id: UUID
    model_id: UUID
    dataset_id: UUID

    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    evaluation_loss: float

    # Classification Metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float

    # 2D Array representing [ [TN, FP], [FN, TP] ]
    confusion_matrix: List[List[int]]

    evaluation_duration_seconds: float
    evaluation_completed: bool

    metadata: Dict[str, Any] = Field(default_factory=dict)
