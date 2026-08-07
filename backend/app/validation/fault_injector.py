from typing import List


class ChaosEngine:
    """
    Systematically injects faults to verify graceful degradation.
    """

    def __init__(self, failure_points: List[str] = None, skip_points: List[str] = None):
        self.failure_points = failure_points or []
        self.skip_points = skip_points or []

    def should_fail(self, stage: str) -> bool:
        return stage in self.failure_points

    def should_skip(self, stage: str) -> bool:
        return stage in self.skip_points
