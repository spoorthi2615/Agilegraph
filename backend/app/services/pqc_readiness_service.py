from app.models.crypto_graph import CryptoGraph
from app.models.pqc_readiness import PQCReadinessAssessment, PQCReadinessLevel
from app.graph.graph_builder import NodeType
from app.models.crypto_asset import AssetType

class PQCReadinessService:
    """
    Service responsible for evaluating an entire CryptoGraph to determine its 
    macro-level readiness for the transition to Post-Quantum Cryptography (PQC).
    """

    # Algorithms vulnerable to quantum attacks (Shor's/Grover's) or classically deprecated
    _CLASSICAL_ALGORITHMS = {
        "RSA", "ECC", "EC", "DES", "3DES", "DESEDE", "MD5", "SHA-1"
    }

    # Symmetric and hashing algorithms currently considered secure in a post-quantum world
    _MODERN_ALGORITHMS = {
        "AES", "SHA-256", "SHA-384", "SHA-512"
    }

    @classmethod
    def assess_readiness(cls, graph: CryptoGraph) -> PQCReadinessAssessment:
        """
        Analyzes the topology and metadata of the CryptoGraph to compute a 
        project-wide PQC readiness score.
        """
        total_assets = 0
        pqc_ready = 0
        classical = 0
        
        for node in graph.nodes.values():
            # Skip structural containers and high-level software dependencies
            if node.node_type in [NodeType.FILE.value, AssetType.DEPENDENCY.value]:
                continue
                
            # Extract the embedded algorithm
            algo = node.metadata.get("algorithm") if node.metadata else None
            
            if not algo:
                # Assets without a discernible algorithm cannot be proven quantum-safe
                total_assets += 1
                classical += 1
                continue
                
            algo_upper = algo.upper()
            
            # Normalize ECC curve names
            if algo_upper.startswith("ECC") or algo_upper.startswith("EC"):
                lookup_algo = "EC"
            else:
                lookup_algo = algo_upper
                
            total_assets += 1
            
            if lookup_algo in cls._MODERN_ALGORITHMS:
                pqc_ready += 1
            elif lookup_algo in cls._CLASSICAL_ALGORITHMS:
                classical += 1
            else:
                # Unrecognized algorithms are treated as classical/vulnerable by default
                classical += 1

        # Calculate the macro-level readiness score
        if total_assets == 0:
            score = 100.0
            summary = "No cryptographic assets detected. Project is trivially PQC ready."
        else:
            score = (pqc_ready / total_assets) * 100.0
            summary = f"Project scored {score:.1f}% readiness. {pqc_ready}/{total_assets} assets are quantum-safe."
            
        level = cls._determine_level(score)
        
        return PQCReadinessAssessment(
            overall_score=round(score, 2),
            readiness_level=level,
            total_crypto_assets=total_assets,
            pqc_ready_assets=pqc_ready,
            classical_assets=classical,
            migration_candidates=classical, # Anything not PQC-ready is a candidate for migration
            summary=summary
        )

    @classmethod
    def _determine_level(cls, score: float) -> PQCReadinessLevel:
        """
        Mathematically categorizes the numeric score into an executive readiness tier.
        """
        if score >= 80:
            return PQCReadinessLevel.READY
        elif score >= 60:
            return PQCReadinessLevel.MOSTLY_READY
        elif score >= 40:
            return PQCReadinessLevel.PARTIALLY_READY
        else:
            return PQCReadinessLevel.NOT_READY
