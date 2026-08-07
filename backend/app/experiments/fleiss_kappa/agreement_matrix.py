from typing import List, Tuple

from app.experiments.expert_validation.expert_label import RiskLabel
from app.experiments.expert_validation.validation_dataset import ValidationDataset


class AgreementMatrixEngine:
    """
    Builds the subject-category N x k agreement matrix for Fleiss' Kappa.
    """

    @staticmethod
    def build(
        dataset: ValidationDataset,
    ) -> Tuple[List[List[int]], List[str], int, int]:
        classes = [
            RiskLabel.LOW.value,
            RiskLabel.MEDIUM.value,
            RiskLabel.HIGH.value,
            RiskLabel.CRITICAL.value,
            RiskLabel.UNKNOWN.value,
        ]
        class_to_idx = {cls: idx for idx, cls in enumerate(classes)}

        matrix = []

        # Filter out records with no expert labels (can't measure agreement on 0 raters)
        valid_records = [r for r in dataset.records if len(r.expert_labels) > 0]

        for record in valid_records:
            row = [0] * len(classes)
            for expert_label in record.expert_labels:
                lbl = expert_label.label.value
                if lbl in class_to_idx:
                    row[class_to_idx[lbl]] += 1
            matrix.append(row)

        n_assets = len(matrix)
        # Use the maximum number of experts on a single asset as a reporting metric
        n_experts = max([sum(row) for row in matrix]) if matrix else 0

        return matrix, classes, n_assets, n_experts
