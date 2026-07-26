import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.fleiss_kappa.fleiss_config import FleissConfig
from app.experiments.fleiss_kappa.fleiss_kappa_service import FleissKappaService
from app.experiments.fleiss_kappa.fleiss_report import FleissReport
from app.experiments.expert_validation.expert_label import ExpertLabel, RiskLabel
from app.experiments.expert_validation.validation_dataset import ValidationDataset, ValidationRecord

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def build_dataset(matrix_str: str) -> ValidationDataset:
    """
    Helper to quickly build datasets from simple strings for statistical testing.
    Matrix str format: "30000, 03000" where digits are frequency counts for L,M,H,C,U.
    """
    records = []
    classes = [RiskLabel.LOW, RiskLabel.MEDIUM, RiskLabel.HIGH, RiskLabel.CRITICAL, RiskLabel.UNKNOWN]
    for i, row in enumerate(matrix_str.split(",")):
        row = row.strip()
        if not row: continue
        labels = []
        expert_counter = 1
        for class_idx, char in enumerate(row):
            count = int(char)
            for _ in range(count):
                labels.append(ExpertLabel(
                    asset_id=f"AST_{i}", 
                    expert_id=f"EXP_{expert_counter}", 
                    label=classes[class_idx], 
                    confidence=100
                ))
                expert_counter += 1
        records.append(ValidationRecord(asset_id=f"AST_{i}", repository="test", expert_labels=labels))
    return ValidationDataset(project_id="test", records=records)

def test_sprint68():
    logging.info("Testing Sprint 68 Fleiss' Kappa Framework...")
    
    config = FleissConfig(output_directory="outputs/fleiss_kappa")
    service = FleissKappaService(config)
    
    # 1. Perfect Agreement (3 raters, 4 subjects, all agree perfectly on different classes)
    ds_perfect = build_dataset("30000, 03000, 00300, 00030")
    res_perfect = service.calculate_kappa(ds_perfect)
    assert res_perfect.kappa_score == 1.0, f"Expected 1.0, got {res_perfect.kappa_score}"
    assert res_perfect.interpretation == "Almost Perfect", "Failed Landis & Koch boundary"
    
    # 2. Poor/Zero Agreement (3 raters, votes completely disjointed)
    # "11100" means 1 L, 1 M, 1 H -> No two experts agreed on anything.
    ds_poor = build_dataset("11100, 01110, 10110, 01011")
    res_poor = service.calculate_kappa(ds_poor)
    assert res_poor.kappa_score <= 0.0, f"Expected negative or 0 kappa, got {res_poor.kappa_score}"
    assert res_poor.interpretation == "Poor", "Failed Landis & Koch boundary for 0.0"
    
    # 3. Variable Reviewers (2 experts on AST_1, 4 on AST_2, 3 on AST_3)
    ds_var = build_dataset("20000, 04000, 00300")
    res_var = service.calculate_kappa(ds_var)
    assert res_var.kappa_score == 1.0, "Failed to calculate variable-rater perfect agreement"
    assert res_var.number_of_experts == 4, "Failed to dynamically extract max experts"
    
    # 4. Filter Missing/Single-Rater Labels (Cannot mathematically form an 'agreement' pair)
    ds_missing = build_dataset("30000, 03000, 10000") # 3rd item has only 1 expert
    res_missing = service.calculate_kappa(ds_missing)
    assert res_missing.number_of_assets == 2, "Failed to safely drop asset lacking 2+ raters"
    
    logging.info(f"Test Perfect:  k={res_perfect.kappa_score:.4f} -> {res_perfect.interpretation}")
    logging.info(f"Test Poor:     k={res_poor.kappa_score:.4f} -> {res_poor.interpretation}")
    logging.info(f"Test Variable: k={res_var.kappa_score:.4f} -> {res_var.interpretation}")
    
    # 5. Generate UTF-8 Bound Report
    FleissReport.generate([res_perfect, res_poor, res_var, res_missing], config.output_directory)
    
    logging.info("All Sprint 68 Fleiss' Kappa tests passed successfully!")

if __name__ == "__main__":
    test_sprint68()
