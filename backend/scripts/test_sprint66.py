import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.experiments.expert_validation.expert import Expert
from app.experiments.expert_validation.expert_label import ExpertLabel, RiskLabel
from app.experiments.expert_validation.validation_dataset import ValidationDataset, ValidationRecord
from app.experiments.expert_validation.validation_config import ValidationConfig
from app.experiments.expert_validation.validation_service import ValidationService
from app.experiments.expert_validation.validation_report import ValidationReport

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint66():
    logging.info("Testing Sprint 66 Expert Validation Framework...")
    
    config = ValidationConfig(
        tie_breaker_strategy="highest_risk",
        drop_unknowns_if_possible=True,
        output_directory="outputs/expert_validation"
    )
    
    service = ValidationService(config)
    
    # 1. Register Experts
    expert_a = Expert(expert_id="EXP_001", years_of_experience=10, area_of_expertise="AppSec")
    expert_b = Expert(expert_id="EXP_002", years_of_experience=15, area_of_expertise="Cryptography")
    expert_c = Expert(expert_id="EXP_003", years_of_experience=5, area_of_expertise="NetworkSec")
    
    service.register_expert(expert_a)
    service.register_expert(expert_b)
    service.register_expert(expert_c)
    
    # Duplicate registration check
    service.register_expert(expert_a)
    
    # 2. Build Mock Validation Dataset
    records = []
    
    # Record 1: Clear Majority (2 HIGH, 1 LOW)
    rec1 = ValidationRecord(
        asset_id="AST_100", repository="repo_alpha", predicted_risk=RiskLabel.HIGH,
        expert_labels=[
            ExpertLabel(asset_id="AST_100", expert_id="EXP_001", label=RiskLabel.HIGH, confidence=90),
            ExpertLabel(asset_id="AST_100", expert_id="EXP_002", label=RiskLabel.HIGH, confidence=95),
            ExpertLabel(asset_id="AST_100", expert_id="EXP_003", label=RiskLabel.LOW, confidence=80),
        ]
    )
    records.append(rec1)
    
    # Record 2: Tie Scenario (1 CRITICAL, 1 MEDIUM) -> Should resolve to CRITICAL (highest risk)
    rec2 = ValidationRecord(
        asset_id="AST_101", repository="repo_alpha", predicted_risk=RiskLabel.CRITICAL,
        expert_labels=[
            ExpertLabel(asset_id="AST_101", expert_id="EXP_001", label=RiskLabel.CRITICAL, confidence=100),
            ExpertLabel(asset_id="AST_101", expert_id="EXP_002", label=RiskLabel.MEDIUM, confidence=80),
        ]
    )
    records.append(rec2)
    
    # Record 3: Missing Review
    rec3 = ValidationRecord(
        asset_id="AST_102", repository="repo_alpha", predicted_risk=RiskLabel.LOW,
        expert_labels=[]
    )
    records.append(rec3)
    
    # Record 4: UNKNOWN filtering (1 UNKNOWN, 2 MEDIUM) -> Should resolve to MEDIUM
    rec4 = ValidationRecord(
        asset_id="AST_103", repository="repo_alpha", predicted_risk=RiskLabel.MEDIUM,
        expert_labels=[
            ExpertLabel(asset_id="AST_103", expert_id="EXP_001", label=RiskLabel.UNKNOWN, confidence=10),
            ExpertLabel(asset_id="AST_103", expert_id="EXP_002", label=RiskLabel.MEDIUM, confidence=85),
            ExpertLabel(asset_id="AST_103", expert_id="EXP_003", label=RiskLabel.MEDIUM, confidence=80),
        ]
    )
    records.append(rec4)
    
    dataset = ValidationDataset(project_id="repo_alpha", records=records)
    
    # 3. Generate Consensus
    resolved_dataset = service.generate_consensus(dataset)
    
    # 4. Verify Outcomes
    r1, r2, r3, r4 = resolved_dataset.records
    
    assert r1.consensus_label == RiskLabel.HIGH, "Majority vote failed"
    assert r1.disagreement_flag is True, "Disagreement flag failed on split vote"
    
    assert r2.consensus_label == RiskLabel.CRITICAL, "Highest risk tie breaker failed"
    assert r2.disagreement_flag is True, "Disagreement flag failed on tie"
    
    assert r3.consensus_label == RiskLabel.UNKNOWN, "Missing review resolution failed"
    assert r3.disagreement_flag is False, "Missing review flagged as disagreement incorrectly"
    
    assert r4.consensus_label == RiskLabel.MEDIUM, "UNKNOWN filtering failed"
    
    # 5. Report Generation
    ValidationReport.generate(resolved_dataset, len(service.experts), config.output_directory)
    
    logging.info("All Sprint 66 Expert Validation Framework tests passed successfully!")

if __name__ == "__main__":
    test_sprint66()
