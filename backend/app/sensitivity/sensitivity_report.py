import json
from typing import List
from app.sensitivity.ranking_stability import RankingStabilityResult

class SensitivityReport:
    """
    Generates reports from the ranking stability engines.
    """
    @staticmethod
    def generate_json(results: List[RankingStabilityResult]) -> str:
        return json.dumps([r.model_dump() for r in results], indent=2)
