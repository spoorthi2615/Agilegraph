import pytest
from app.heuristics.heuristic_breakdown import HeuristicBreakdown
from app.heuristics.migration_estimator import MigrationEstimator
from app.heuristics.recommendation_engine import RecommendationEngine

def test_migration_estimator_reduction():
    estimator = MigrationEstimator()
    reduction = estimator.estimate_reduction(
        current_total_score=80.0,
        algorithm_penalty=40.0,
        certificate_penalty=10.0
    )
    assert reduction.absolute_reduction > 0
    assert reduction.percentage_reduction > 0.0

def test_recommendation_engine_prioritization():
    engine = RecommendationEngine()
    breakdown = HeuristicBreakdown(
        asset_id="RSA-2048-Asset",
        data_sensitivity_score=30.0,
        exposure_level_score=20.0,
        algorithm_strength_penalty=40.0,
        certificate_weakness_penalty=0.0,
        network_centrality_score=10.0,
        total_score=80.0,
        is_pqc_ready=False,
        migration_effort="Medium"
    )
    
    gnn_preds = {"RSA-2048-Asset": 0.9}
    recs = engine.generate_recommendations([breakdown], gnn_preds)
    
    assert len(recs) == 1
    assert recs[0].asset_id == "RSA-2048-Asset"
    assert recs[0].suggested_replacement == "Kyber-768 / ML-KEM"
    assert recs[0].priority_score > 0

def test_migration_estimator_zero_reduction():
    estimator = MigrationEstimator()
    reduction = estimator.estimate_reduction(
        current_total_score=10.0,
        algorithm_penalty=0.0,
        certificate_penalty=0.0
    )
    assert reduction.absolute_reduction == 0.0
    assert reduction.percentage_reduction == 0.0

def test_recommendation_engine_pqc_ready_skip():
    engine = RecommendationEngine()
    breakdown = HeuristicBreakdown(
        asset_id="ML-KEM-Asset",
        data_sensitivity_score=10.0,
        exposure_level_score=0.0,
        algorithm_strength_penalty=0.0,
        certificate_weakness_penalty=0.0,
        network_centrality_score=0.0,
        total_score=10.0,
        is_pqc_ready=True,
        migration_effort="Low"
    )
    recs = engine.generate_recommendations([breakdown], {})
    assert len(recs) == 0

def test_recommendation_engine_symmetric_replacement():
    engine = RecommendationEngine()
    breakdown = HeuristicBreakdown(
        asset_id="AES-128-Asset",
        data_sensitivity_score=20.0,
        exposure_level_score=10.0,
        algorithm_strength_penalty=30.0,
        certificate_weakness_penalty=0.0,
        network_centrality_score=0.0,
        total_score=60.0,
        is_pqc_ready=False,
        migration_effort="Low"
    )
    recs = engine.generate_recommendations([breakdown], {"AES-128-Asset": 0.5})
    assert len(recs) == 1
    assert recs[0].suggested_replacement == "AES-256-GCM / SHA-3"
