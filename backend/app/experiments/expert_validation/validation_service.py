import logging
from collections import Counter
from typing import Dict

from app.experiments.expert_validation.expert import Expert
from app.experiments.expert_validation.expert_label import RiskLabel
from app.experiments.expert_validation.validation_config import ValidationConfig
from app.experiments.expert_validation.validation_dataset import ValidationDataset

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Orchestrates expert registration, label ingestion, and the mathematically rigorous Majority Voting consensus algorithm.
    """

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.experts: Dict[str, Expert] = {}

    def register_expert(self, expert: Expert):
        if expert.expert_id in self.experts:
            logger.warning(f"Expert {expert.expert_id} is already registered. Overwriting.")
        self.experts[expert.expert_id] = expert

    def generate_consensus(self, dataset: ValidationDataset) -> ValidationDataset:
        """
        Executes the Majority Voting algorithm and handles ties across the dataset.
        """
        risk_hierarchy = {
            RiskLabel.UNKNOWN: 0,
            RiskLabel.LOW: 1,
            RiskLabel.MEDIUM: 2,
            RiskLabel.HIGH: 3,
            RiskLabel.CRITICAL: 4,
        }

        for record in dataset.records:
            # 1. Missing Reviews
            if not record.expert_labels:
                record.consensus_label = RiskLabel.UNKNOWN
                record.disagreement_flag = False
                continue

            labels_to_consider = [l.label for l in record.expert_labels]

            # 2. Unknown Handling
            if self.config.drop_unknowns_if_possible:
                valid_labels = [lbl for lbl in labels_to_consider if lbl != RiskLabel.UNKNOWN]
                if valid_labels:
                    labels_to_consider = valid_labels

            if not labels_to_consider:
                record.consensus_label = RiskLabel.UNKNOWN
                record.disagreement_flag = False
                continue

            # 3. Majority Voting
            counts = Counter(labels_to_consider)
            max_votes = max(counts.values())
            candidates = [lbl for lbl, count in counts.items() if count == max_votes]

            # Flag disagreement if experts cast differing valid votes
            if (
                len(set([l.label for l in record.expert_labels if l.label != RiskLabel.UNKNOWN]))
                > 1
            ):
                record.disagreement_flag = True

            # 4. Tie Breaker Resolution
            if len(candidates) == 1:
                record.consensus_label = candidates[0]
            else:
                if self.config.tie_breaker_strategy == "highest_risk":
                    record.consensus_label = max(candidates, key=lambda l: risk_hierarchy[l])
                elif self.config.tie_breaker_strategy == "unknown":
                    record.consensus_label = RiskLabel.UNKNOWN
                else:
                    record.consensus_label = max(candidates, key=lambda l: risk_hierarchy[l])

        return dataset
