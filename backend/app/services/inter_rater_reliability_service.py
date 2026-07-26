from datetime import datetime, timezone
from app.models.expert_validation import ExpertValidation
from app.models.inter_rater_reliability import InterRaterReliability, KappaInterpretation

class InterRaterReliabilityService:
    """
    Service responsible for rigorously computing Cohen's Kappa to measure inter-rater 
    reliability between exactly two cybersecurity experts assessing a single node.
    """

    @classmethod
    def calculate_kappa(
        cls, 
        validation_1: ExpertValidation, 
        validation_2: ExpertValidation
    ) -> InterRaterReliability:
        """
        Executes the mathematical Cohen's Kappa formula (Observed vs Expected Agreement) 
        and maps the resulting score to a standardized interpretation string.
        """
        
        # 1. Reject different node_ids
        if validation_1.node_id != validation_2.node_id:
            raise ValueError(
                f"Mixed nodes detected. Expected both experts to evaluate the same node, "
                f"but found {validation_1.node_id} and {validation_2.node_id}."
            )
            
        # 2. Validate exactly two distinct experts
        if validation_1.expert_id == validation_2.expert_id:
            raise ValueError("Cohen's Kappa requires exactly two distinct experts. Found identical expert IDs.")
            
        label_1 = validation_1.expert_label
        label_2 = validation_2.expert_label
        
        # 3. Calculate Observed Agreement (Po)
        # For a single node, observed agreement is either exactly 1.0 (match) or 0.0 (mismatch)
        is_agreement = (label_1 == label_2)
        p_o = 1.0 if is_agreement else 0.0
        
        # 4. Calculate Expected Agreement (Pe) based on marginal probabilities
        # Given N=1 sample, the marginal probabilities are degenerate (either 1.0 or 0.0).
        unique_labels = set([label_1, label_2])
        p_e = 0.0
        
        for label in unique_labels:
            prob_1 = 1.0 if label_1 == label else 0.0
            prob_2 = 1.0 if label_2 == label else 0.0
            p_e += (prob_1 * prob_2)
            
        # 5. Compute Cohen's Kappa
        # Formula: k = (Po - Pe) / (1 - Pe)
        if (1.0 - p_e) == 0.0:
            # Handle division by zero when experts are in perfect expected alignment
            kappa = 1.0 if is_agreement else 0.0
        else:
            kappa = (p_o - p_e) / (1.0 - p_e)
            
        # 6. Determine Interpretation (Landis and Koch thresholds)
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
            node_id=validation_1.node_id,
            expert_1_id=validation_1.expert_id,
            expert_2_id=validation_2.expert_id,
            cohens_kappa=kappa,
            observed_agreement=p_o,
            expected_agreement=p_e,
            interpretation=interpretation,
            calculated_at=datetime.now(timezone.utc),
            metadata={
                "validation_1_id": str(validation_1.validation_id),
                "validation_2_id": str(validation_2.validation_id)
            }
        )
