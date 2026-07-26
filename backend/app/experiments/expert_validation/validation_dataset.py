from pydantic import BaseModel
from typing import List, Optional
from app.experiments.expert_validation.expert_label import ExpertLabel, RiskLabel

class ValidationRecord(BaseModel):
    """
    Consolidates the machine's prediction and the human experts' labels for a specific asset.
    """
    asset_id: str
    repository: str
    predicted_risk: Optional[RiskLabel] = None
    expert_labels: List[ExpertLabel] = []
    
    # These fields are populated post-consensus resolution
    consensus_label: Optional[RiskLabel] = None
    disagreement_flag: bool = False

class ValidationDataset(BaseModel):
    """
    Container for all validation records in a repository.
    """
    project_id: str
    records: List[ValidationRecord] = []
