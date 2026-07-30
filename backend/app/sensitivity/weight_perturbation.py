from pydantic import BaseModel
from typing import Dict, List
import copy

class PerturbationPayload(BaseModel):
    id: str
    description: str
    weights: Dict[str, float]

class WeightPerturbator:
    """
    Generates perturbed heuristic weight matrices without mutating the baseline.
    """
    def generate_single_weight_perturbations(self, baseline_weights: Dict[str, float], scales: List[float]) -> List[PerturbationPayload]:
        payloads = []
        for key, base_val in baseline_weights.items():
            for scale in scales:
                new_weights = copy.deepcopy(baseline_weights)
                # Weights are clamped to 0 minimum
                new_weights[key] = max(0.0, base_val * (1.0 + scale))
                payloads.append(PerturbationPayload(
                    id=f"{key}_scale_{scale}",
                    description=f"Perturbed {key} by {scale*100:.0f}%",
                    weights=new_weights
                ))
        return payloads
        
    def generate_all_weights_perturbations(self, baseline_weights: Dict[str, float], scales: List[float]) -> List[PerturbationPayload]:
        payloads = []
        for scale in scales:
            new_weights = {}
            for key, base_val in baseline_weights.items():
                new_weights[key] = max(0.0, base_val * (1.0 + scale))
            payloads.append(PerturbationPayload(
                id=f"all_scale_{scale}",
                description=f"Perturbed ALL weights simultaneously by {scale*100:.0f}%",
                weights=new_weights
            ))
        return payloads
