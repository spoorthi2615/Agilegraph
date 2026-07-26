from datetime import datetime, timezone
from app.models.inference_result import InferenceResult
from app.models.expert_validation import ExpertValidation

class ExpertValidationService:
    """
    Service responsible for rigorously comparing an AI's cryptographic risk prediction
    against a human cybersecurity expert's ground-truth assessment.
    """

    @classmethod
    def validate_prediction(
        cls,
        inference_result: InferenceResult,
        expert_id: str,
        expert_name: str,
        node_id: str,
        expert_risk_score: float,
        expert_label: int,
        comments: str = None
    ) -> ExpertValidation:
        """
        Locates the AI prediction for a specific node, compares it mathematically against
        the expert's assessment, and returns an immutable ExpertValidation record.
        """
        # 1. Locate the exact AI prediction for the given node
        target_prediction = None
        for prediction in inference_result.node_predictions:
            if prediction.node_id == node_id:
                target_prediction = prediction
                break
                
        if target_prediction is None:
            raise ValueError(f"Node UUID {node_id} was not found within the provided InferenceResult.")
            
        # 2. Extract AI predictions
        ai_risk_score = target_prediction.risk_score
        ai_label = target_prediction.label
        
        # 3. Compute score difference (absolute mathematical variance)
        score_difference = abs(ai_risk_score - expert_risk_score)
        
        # 4. Determine label agreement (strict categorical match)
        agreement = (ai_label == expert_label)
        
        # 5. Create immutable validation record
        return ExpertValidation(
            expert_id=expert_id,
            expert_name=expert_name,
            node_id=node_id,
            ai_risk_score=ai_risk_score,
            expert_risk_score=expert_risk_score,
            ai_label=ai_label,
            expert_label=expert_label,
            agreement=agreement,
            score_difference=score_difference,
            comments=comments,
            validated_at=datetime.now(timezone.utc),
            metadata={
                "inference_id": str(inference_result.inference_id),
                "model_id": str(inference_result.model_id),
                "dataset_id": str(inference_result.dataset_id)
            }
        )
