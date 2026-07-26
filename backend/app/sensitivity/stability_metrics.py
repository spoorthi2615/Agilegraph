from typing import List

class StabilityMetrics:
    """
    Pure Python implementations of non-parametric ranking statistics.
    Avoids heavy Pandas/SciPy dependencies solely for array math.
    """
    @staticmethod
    def spearman_rank_correlation(base_ranks: List[str], perturbed_ranks: List[str]) -> float:
        """
        Calculates Spearman's rho.
        Assumes both lists contain the exact same elements, just reordered.
        """
        n = len(base_ranks)
        if n <= 1:
            return 1.0
            
        base_map = {item: i for i, item in enumerate(base_ranks)}
        pert_map = {item: i for i, item in enumerate(perturbed_ranks)}
        
        sum_d_squared = sum((base_map[item] - pert_map[item]) ** 2 for item in base_ranks)
        
        rho = 1.0 - (6.0 * sum_d_squared) / (n * (n**2 - 1))
        return rho

    @staticmethod
    def top_k_overlap(base_ranks: List[str], perturbed_ranks: List[str], k: int) -> float:
        """
        Calculates the percentage overlap of the top-K elements.
        """
        if not base_ranks:
            return 1.0
            
        top_k_base = set(base_ranks[:k])
        top_k_pert = set(perturbed_ranks[:k])
        
        if not top_k_base:
            return 1.0
            
        overlap = len(top_k_base.intersection(top_k_pert))
        return overlap / len(top_k_base)
