from datetime import datetime, timezone
from typing import List, Set

from app.models.expert_validation import ExpertValidation
from app.models.inter_rater_reliability import InterRaterReliability, KappaInterpretation


class InterRaterReliabilityService:
    """
    Service responsible for rigorously computing Fleiss' Kappa to measure inter-rater
    reliability across multiple cybersecurity experts assessing a batch of nodes.
    """

    @classmethod
    def calculate_fleiss_kappa(
        cls, validations_batch: List[List[ExpertValidation]]
    ) -> InterRaterReliability:
        """
        Executes the mathematical Fleiss' Kappa formula for N subjects and n raters.
        Maps the resulting score to a standardized interpretation string.

        Args:
            validations_batch: A list of subjects. Each subject is a list of validations
                               performed by different experts on that subject.
        """

        N = len(validations_batch)
        if N == 0:
            raise ValueError("No validations provided. Cannot compute Fleiss' Kappa.")

        # Ensure consistent number of raters
        n = len(validations_batch[0])
        if n < 2:
            raise ValueError("Fleiss' Kappa requires at least 2 raters per subject.")

        expert_ids: Set[str] = set()

        # Discover all unique categories (labels)
        categories = set()
        for subject_validations in validations_batch:
            if len(subject_validations) != n:
                raise ValueError("Inconsistent number of raters across subjects.")
            for val in subject_validations:
                categories.add(val.expert_label)
                expert_ids.add(val.expert_id)

        category_list = list(categories)
        k = len(category_list)

        # Calculate n_ij (number of raters who assigned subject i to category j)
        n_ij = [[0] * k for _ in range(N)]
        for i, subject_validations in enumerate(validations_batch):
            for val in subject_validations:
                j = category_list.index(val.expert_label)
                n_ij[i][j] += 1

        # Calculate P_j (proportion of all assignments to category j)
        P_j = [0.0] * k
        for j in range(k):
            column_sum = sum(n_ij[i][j] for i in range(N))
            P_j[j] = column_sum / (N * n)

        P_e = sum(pj**2 for pj in P_j)

        # Calculate P_i (extent of agreement on subject i)
        P_i = [0.0] * N
        for i in range(N):
            row_sum_squares = sum(n_ij[i][j] ** 2 for j in range(k))
            # Formula: (sum(n_ij^2) - n) / (n * (n - 1))
            P_i[i] = (row_sum_squares - n) / (n * (n - 1))

        P_bar = sum(P_i) / N

        # Compute Fleiss' Kappa
        if (1.0 - P_e) == 0.0:
            # Degenerate case: raters agreed on one category universally
            kappa = 1.0 if P_bar == 1.0 else 0.0
        else:
            kappa = (P_bar - P_e) / (1.0 - P_e)

        # Interpretation
        if kappa < 0.0:
            interpretation = KappaInterpretation.POOR
        elif kappa <= 0.20:
            interpretation = KappaInterpretation.SLIGHT
        elif kappa <= 0.40:
            interpretation = KappaInterpretation.FAIR
        elif kappa <= 0.60:
            interpretation = KappaInterpretation.MODERATE
        elif kappa <= 0.80:
            interpretation = KappaInterpretation.SUBSTANTIAL
        else:
            interpretation = KappaInterpretation.ALMOST_PERFECT

        return InterRaterReliability(
            expert_ids=list(expert_ids),
            total_subjects=N,
            fleiss_kappa=kappa,
            observed_agreement=P_bar,
            expected_agreement=P_e,
            interpretation=interpretation,
            calculated_at=datetime.now(timezone.utc),
            metadata={"raters_per_subject": n, "categories": category_list},
        )
