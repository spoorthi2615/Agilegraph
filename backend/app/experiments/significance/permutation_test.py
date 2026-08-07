import logging
import math
import random
from typing import List, Tuple

logger = logging.getLogger(__name__)


class PermutationTest:
    """
    Core mathematical algorithm for the Paired Permutation Test.
    Evaluates whether the mean of 'a' (AgileGraph) is significantly greater than the mean of 'b' (Baseline).
    This establishes a directional one-tailed test.
    """

    @staticmethod
    def execute(a: List[float], b: List[float], permutations: int) -> Tuple[float, float, float]:
        """
        Executes the non-parametric permutations.
        Returns: (observed_difference, p_value, effect_size)
        """
        if not a or not b or len(a) != len(b):
            raise ValueError(
                "Input arrays must be non-empty and of equal length to perform paired tests."
            )

        n = len(a)
        diffs = [a[i] - b[i] for i in range(n)]

        obs_diff = sum(diffs) / n

        # Effect size (Cohen's d approximation for paired samples: mean_diff / std_dev(diffs))
        variance = sum((d - obs_diff) ** 2 for d in diffs) / (n - 1) if n > 1 else 0.0
        std_dev = math.sqrt(variance) if variance > 0 else 0.0
        effect_size = obs_diff / std_dev if std_dev > 0 else 0.0

        count_greater_equal = 0

        # Optimization: cache the differences locally
        for _ in range(permutations):
            # Randomly flip signs of differences (mathematically equivalent to swapping a_i and b_i)
            # random.getrandbits(1) is highly optimized in native python compared to random.random()
            perm_sum = sum(d if random.getrandbits(1) else -d for d in diffs)
            perm_mean = perm_sum / n

            if perm_mean >= obs_diff:
                count_greater_equal += 1

        # Calculate one-tailed p-value
        # Adding 1 to numerator and denominator provides the standard unbiased permutation estimator
        p_value = (count_greater_equal + 1) / (permutations + 1)

        return obs_diff, p_value, effect_size
