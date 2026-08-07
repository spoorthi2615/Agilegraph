import datetime


class RiskCalculator:
    def __init__(self, quantum_arrival_year: int = 2030):
        self.quantum_arrival_year = quantum_arrival_year
        self.current_year = datetime.datetime.now().year

    def calculate_base_risk(
        self,
        algorithm: str,
        data_shelf_life_years: int,
        migration_time_years: int,
        data_sensitivity_score: float = 1.0,
    ) -> float:
        """
        Calculate base cryptographic risk score (0.0 to 1.0).
        Formula based on Mosca's Theorem (Data Shelf Life + Migration Time > Time to Quantum = Critical Risk).
        Includes Data Sensitivity modifier (BlastRadius is computed structurally by the GNN).
        """
        time_to_quantum = max(1, self.quantum_arrival_year - self.current_year)

        # Explicit set of known labels emitted by cert_scanner and code_scanner
        explicit_weak = {"RSA", "ECC", "DSA", "EDDSA", "MD5", "SHA1", "DES", "RC4"}
        explicit_safe = {"AES", "CHACHA20"}

        algo_upper = algorithm.upper()

        if algo_upper in explicit_weak:
            is_weak = True
        elif algo_upper in explicit_safe:
            is_weak = False
        elif algo_upper == "UNKNOWN":
            is_weak = True  # Assume risk for unknown algorithms
        else:
            raise ValueError(
                f"Unclassified algorithm detected: {algorithm}. Cannot silently fall through."
            )

        if not is_weak:
            return 0.1 * data_sensitivity_score

        mosca_ratio = (data_shelf_life_years + migration_time_years) / time_to_quantum

        # Combine Mosca's ratio with data sensitivity
        risk_score = mosca_ratio * data_sensitivity_score

        # Normalize between 0.0 and 1.0
        return min(1.0, max(0.0, risk_score))

    def evaluate_certificate_risk(self, expiry_date_str: str, algorithm: str) -> float:
        """
        Evaluate risk of a certificate based on expiry (YYYY-MM-DD string) and algorithm.
        """
        expiry_date = datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        if (expiry_date - datetime.date.today()).days < 0:
            return 1.0  # Expired is immediate critical risk

        # Treat certificate rotation as a fast migration (0.5 years max usually)
        base_risk = self.calculate_base_risk(
            algorithm, data_shelf_life_years=1, migration_time_years=0.5
        )
        return base_risk
