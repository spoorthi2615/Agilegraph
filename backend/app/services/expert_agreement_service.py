from typing import List
from collections import Counter
import statistics
from datetime import datetime, timezone
from app.models.expert_validation import ExpertValidation
from app.models.expert_agreement import ExpertAgreement

class ExpertAgreementService:
    """
    Service responsible for rigorously aggregating and analyzing the mathematical agreement 
    (or disagreement) among multiple cybersecurity experts for a single graph node.
    """

    @classmethod
    def analyze_agreement(
        cls, 
        validations: List[ExpertValidation], 
        consensus_threshold: float = 75.0
    ) -> ExpertAgreement:
        """
        Executes majority voting, computes score variance, and determines consensus 
        across an array of independent expert assessments.
        """
        if not validations:
            raise ValueError("Cannot calculate agreement on an empty list of validations.")
            
        # 1. Reject Mixed Nodes
        # Mathematically invalid to aggregate opinions regarding different source code files.
        target_node_id = validations[0].node_id
        for v in validations:
            if v.node_id != target_node_id:
                raise ValueError(
                    f"Mixed nodes detected. Expected {target_node_id}, found {v.node_id}. "
                    "Agreement can only be computed across validations for a single node."
                )
                
        # 2. Collect Discrete Labels and Continuous Scores
        expert_labels = [v.expert_label for v in validations]
        expert_scores = [v.expert_risk_score for v in validations]
        
        total_experts = len(validations)
        
        # 3. Determine Majority Label via frequency counting
        label_counts = Counter(expert_labels)
        max_count = max(label_counts.values())
        tied_labels = [label for label, count in label_counts.items() if count == max_count]
        
        # Tie-breaker: Select the highest-risk label (maximum integer value)
        majority_label = max(tied_labels)
        majority_count = max_count
        
        # 4. Calculate Agreement Percentage
        agreement_percentage = (majority_count / total_experts) * 100.0
        
        # 5. Determine Consensus
        consensus_reached = agreement_percentage >= consensus_threshold
        
        # 6. Compute Average Expert Score
        average_score = sum(expert_scores) / total_experts
        
        # 7. Compute Score Variance (Requires at least 2 data points)
        if total_experts > 1:
            score_variance = statistics.variance(expert_scores)
        else:
            score_variance = 0.0
            
        # 8. Create immutable agreement record
        return ExpertAgreement(
            node_id=target_node_id,
            total_experts=total_experts,
            agreement_percentage=agreement_percentage,
            majority_label=majority_label,
            consensus_reached=consensus_reached,
            expert_labels=expert_labels,
            expert_scores=expert_scores,
            average_score=average_score,
            score_variance=score_variance,
            calculated_at=datetime.now(timezone.utc),
            metadata={
                "validation_ids": [str(v.validation_id) for v in validations],
                "consensus_threshold_used": consensus_threshold
            }
        )
