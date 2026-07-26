import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.cohens_kappa.kappa_config import KappaConfig
from app.experiments.cohens_kappa.cohens_kappa_service import CohensKappaService
from app.experiments.cohens_kappa.kappa_report import KappaReport
from app.experiments.expert_validation.expert_label import RiskLabel

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint67():
    logging.info("Testing Sprint 67 Cohen's Kappa Framework...")
    
    config = KappaConfig(output_directory="outputs/cohens_kappa")
    service = CohensKappaService(config)
    
    L = RiskLabel.LOW.value
    M = RiskLabel.MEDIUM.value
    H = RiskLabel.HIGH.value
    C = RiskLabel.CRITICAL.value
    U = RiskLabel.UNKNOWN.value
    
    # 1. Perfect Agreement (Kappa = 1.0, Almost Perfect)
    arr_a = [C, C, H, H, M, M, L, L]
    arr_b = [C, C, H, H, M, M, L, L]
    res1 = service.calculate_kappa("AgileGraph", "Expert_1", arr_a, arr_b)
    
    assert res1.kappa_score == 1.0, f"Expected 1.0, got {res1.kappa_score}"
    assert res1.interpretation == "Almost Perfect", f"Expected Almost Perfect, got {res1.interpretation}"
    
    # 2. Complete Disagreement (Kappa <= 0, Poor)
    arr_c = [L, L, L, L, L, L, L, L]
    arr_d = [C, C, C, C, C, C, C, C]
    res2 = service.calculate_kappa("AgileGraph", "Expert_2", arr_c, arr_d)
    
    assert res2.kappa_score <= 0.0, f"Expected negative or zero kappa, got {res2.kappa_score}"
    assert res2.interpretation == "Poor", f"Expected Poor, got {res2.interpretation}"
    
    # 3. Partial Agreement (Moderate boundaries)
    arr_e = [C, C, C, H, M, M, L, L, U, U]
    arr_f = [C, C, H, H, H, M, L, L, M, U]
    res3 = service.calculate_kappa("Expert_1", "Expert_2", arr_e, arr_f)
    
    assert 0.41 <= res3.kappa_score <= 0.80, f"Expected Moderate/Substantial, got {res3.kappa_score}"
    
    # 4. Single-Class Edge Case (Pe = 1.0)
    arr_g = [C, C, C, C]
    arr_h = [C, C, C, C]
    res4 = service.calculate_kappa("Model_A", "Model_B", arr_g, arr_h)
    assert res4.kappa_score == 1.0, "Failed to handle single class identical arrays correctly"
    
    # Log Results
    logging.info(f"Test 1 (Perfect): k={res1.kappa_score:.4f} -> {res1.interpretation}")
    logging.info(f"Test 2 (Disjoint): k={res2.kappa_score:.4f} -> {res2.interpretation}")
    logging.info(f"Test 3 (Partial): k={res3.kappa_score:.4f} -> {res3.interpretation}")
    
    # Generate Report
    KappaReport.generate([res1, res2, res3, res4], config.output_directory)
    
    # 5. Invalid handling test (empty arrays)
    try:
        service.calculate_kappa("A", "B", [], [])
        assert False, "Should have raised ValueError for empty list"
    except ValueError:
        logging.info("Properly caught empty dataset exception.")
        
    logging.info("All Sprint 67 Cohen's Kappa tests passed successfully!")

if __name__ == "__main__":
    test_sprint67()
