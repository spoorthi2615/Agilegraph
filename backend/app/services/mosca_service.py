from typing import Any, Dict


class MoscaService:
    """
    Service implementing Mosca's Theorem (x + y > z) to evaluate
    quantum risk urgency.

    Variables:
    x: Security shelf-life (years data must remain secure)
    y: Migration time (years required to transition to quantum-safe crypto)
    z: Threat horizon (years until cryptographically relevant quantum computers exist)
    """

    @classmethod
    def calculate_index(cls, x: float, y: float, z: float) -> Dict[str, Any]:
        """
        Calculates the Mosca Readiness Index and returns a rich dictionary for the dashboard.
        """
        buffer = round(z - (x + y), 2)
        is_ready = buffer >= 0

        if buffer < 0:
            status = "Critical"
            recommendation = (
                "Begin PQC migration immediately. Threat horizon is shorter "
                "than your security requirements and migration timeline."
            )
        elif buffer == 0:
            status = "Warning"
            recommendation = "Migration must begin immediately to avoid data exposure."
        elif buffer <= 3:
            status = "Elevated"
            recommendation = "Begin planning PQC migration. Buffer is thin."
        else:
            status = "Safe"
            recommendation = "Current timeline is secure, but monitor quantum advancements."

        return {
            "mosca_ready": is_ready,
            "status": status,
            "x": x,
            "y": y,
            "z": z,
            "buffer": buffer,
            "recommendation": recommendation,
        }
