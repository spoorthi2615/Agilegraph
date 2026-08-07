import logging
from typing import List

from pydantic import BaseModel

from app.sensitivity.stability_metrics import StabilityMetrics

logger = logging.getLogger(__name__)


class RankingStabilityResult(BaseModel):
    perturbation_id: str
    spearman_rho: float
    top_10_overlap: float
    top_20_overlap: float
    mean_rank_difference: float
    max_rank_difference: int


class RankingStabilityEngine:
    """
    Calculates stability metrics across baseline vs perturbed heuristic rankings.
    """

    def calculate_stability(
        self, perturbation_id: str, base_ranking: List[str], perturbed_ranking: List[str]
    ) -> RankingStabilityResult:
        n = len(base_ranking)

        if n == 0:
            return RankingStabilityResult(
                perturbation_id=perturbation_id,
                spearman_rho=1.0,
                top_10_overlap=1.0,
                top_20_overlap=1.0,
                mean_rank_difference=0.0,
                max_rank_difference=0,
            )

        rho = StabilityMetrics.spearman_rank_correlation(base_ranking, perturbed_ranking)
        top_10 = StabilityMetrics.top_k_overlap(base_ranking, perturbed_ranking, k=10)
        top_20 = StabilityMetrics.top_k_overlap(base_ranking, perturbed_ranking, k=20)

        base_map = {item: i for i, item in enumerate(base_ranking)}
        pert_map = {item: i for i, item in enumerate(perturbed_ranking)}

        diffs = [abs(base_map[item] - pert_map[item]) for item in base_ranking]

        mean_diff = sum(diffs) / n if n > 0 else 0.0
        max_diff = max(diffs) if n > 0 else 0

        return RankingStabilityResult(
            perturbation_id=perturbation_id,
            spearman_rho=rho,
            top_10_overlap=top_10,
            top_20_overlap=top_20,
            mean_rank_difference=mean_diff,
            max_rank_difference=max_diff,
        )
