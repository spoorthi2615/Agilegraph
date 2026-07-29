from typing import List, Tuple
from app.experiments.expert_validation.expert_label import RiskLabel

class ConfusionMatrixEngine:
    """
    Optimized native Python matrix builder that aggregates predictions into a paired frequency matrix.
    """
    @staticmethod
    def build(a_labels: List[str], b_labels: List[str], classes_override: List[str] = None) -> Tuple[List[List[int]], List[str]]:
        if not a_labels or not b_labels or len(a_labels) != len(b_labels):
            raise ValueError("Label arrays must be non-empty and of equal length.")
            
        if classes_override:
            classes = classes_override
        else:
            classes = sorted(list(set(a_labels) | set(b_labels)))
            
        class_to_idx = {cls: idx for idx, cls in enumerate(classes)}
        
        n = len(classes)
        matrix = [[0] * n for _ in range(n)]
        
        for a, b in zip(a_labels, b_labels):
            # Only count valid recognized labels
            if a in class_to_idx and b in class_to_idx:
                matrix[class_to_idx[a]][class_to_idx[b]] += 1
                
        return matrix, classes
