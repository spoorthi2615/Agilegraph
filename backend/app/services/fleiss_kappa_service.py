from typing import List
from collections import Counter
from datetime import datetime, timezone

from app.models.expert_validation import ExpertValidation
from app.models.multi_rater_reliability import MultiRaterReliability
from app.models.inter_rater_reliability import KappaInterpretation

class FleissKappaService:
    """
    Service responsible for computing Fleiss' Kappa to measure the statistical reliability 
    of agreement among three or more cybersecurity experts evaluating a single node.
    """

    @classmethod
    def calculate_kappa(cls, validations: List[ExpertValidation]) -> MultiRaterReliability:
        """
        Executes the mathematical Fleiss' Kappa formula for N >= 3 raters on a single item.
        Determines the proportion of observed agreement over chance agreement.
        """
        
        # 1. Validate minimum 3 experts
        if not validations or len(validations) < 3:
            raise ValueError(f"Fleiss' Kappa mathematically requires at least 3 experts. Found {len(validations)}.")
            
        # 2. Reject different node_ids to ensure referential integrity
        target_node_id = validations[0].node_id
        expert_ids = []
        labels = []
        
        for v in validations:
            if v.node_id != target_node_id:
                raise ValueError(
                    f"Mixed nodes detected. Expected {target_node_id}, found {v.node_id}. "
                    "Fleiss' Kappa can only be computed across validations for a single node."
                )
            expert_ids.append(v.expert_id)
            labels.append(v.expert_label)
            
        # Validate unique raters (cannot have the same expert vote twice)
        if len(set(expert_ids)) != len(expert_ids):
            raise ValueError("Duplicate expert IDs found. Each validation must originate from a distinct expert.")
            
        n_raters = len(validations)
        
        # 3. Calculate Observed Agreement (Po) for a single item
        # Formula: P_i = [sum(n_ij^2) - n] / [n * (n - 1)] 
        # where n_ij is the number of raters who assigned the item to category j.
        label_counts = Counter(labels)
        
        sum_of_squares = sum(count ** 2 for count in label_counts.values())
        p_o = (sum_of_squares - n_raters) / (n_raters * (n_raters - 1))
        
        # 4. Calculate Expected Agreement (Pe) based on marginals
        # For a single item, p_j = n_ij / n_raters
        # Pe = sum(p_j^2)
        p_e = sum((count / n_raters) ** 2 for count in label_counts.values())
        
        # 5. Compute Fleiss' Kappa
        # Formula: k = (Po - Pe) / (1 - Pe)
        if (1.0 - p_e) == 0.0:
            # Prevent division by zero if all experts perfectly aligned on the same label
            kappa = 1.0 if p_o == 1.0 else 0.0
        else:
            kappa = (p_o - p_e) / (1.0 - p_e)
            
        # 6. Determine Interpretation using Landis & Koch standard thresholds
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
            
        return MultiRaterReliability(
            node_id=target_node_id,
            expert_ids=expert_ids,
            total_experts=n_raters,
            fleiss_kappa=kappa,
            observed_agreement=p_o,
            expected_agreement=p_e,
            interpretation=interpretation,
            calculated_at=datetime.now(timezone.utc),
            metadata={
                "validation_ids": [str(v.validation_id) for v in validations]
            }
        )
