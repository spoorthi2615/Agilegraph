import pytest
from report_helpers import compare_performance, generate_heterogeneous_ablation_text, generate_gatv2_ablation_text, get_f1_value, get_best_model_name

def test_compare_performance():
    assert compare_performance("Model A", 0.8, "Model B", 0.5) == "Model A outperformed Model B"
    assert compare_performance("Model A", 0.5, "Model B", 0.8) == "Model A underperformed relative to Model B"
    assert compare_performance("Model A", 0.5, "Model B", 0.5) == "Model A performed comparably to Model B"

def test_generate_heterogeneous_ablation_text():
    # Test Homogeneous beats Full Model
    res = generate_heterogeneous_ablation_text(no_het_f1=0.8, full_f1=0.5)
    assert "actually outperformed the Full Model" in res
    assert "added unnecessary noise or caused overfitting" in res
    
    # Test Full Model beats Homogeneous
    res2 = generate_heterogeneous_ablation_text(no_het_f1=0.5, full_f1=0.8)
    assert "underperformed the Full Model" in res2
    assert "provides crucial structural priors" in res2
    
    # Test tie
    res3 = generate_heterogeneous_ablation_text(no_het_f1=0.5, full_f1=0.5)
    assert "performed identically to the Full Model" in res3

def test_generate_gatv2_ablation_text():
    # Test GCN beats GATv2
    res = generate_gatv2_ablation_text(no_gat_f1=0.8, full_f1=0.5)
    assert "outperforming the Full Model" in res
    assert "provides minimal to no benefit" in res
    
    # Test GATv2 beats GCN
    res2 = generate_gatv2_ablation_text(no_gat_f1=0.5, full_f1=0.8)
    assert "significant performance drop" in res2
    assert "highly beneficial for resolving complex transitive risk" in res2
    
    # Test tie
    res3 = generate_gatv2_ablation_text(no_gat_f1=0.5, full_f1=0.5)
    assert "identical F1" in res3

def test_get_best_model_name():
    results_mock = {
        "ablation_f1": {
            "Model A": {"mean": 0.5, "std": 0.1},
            "Model B": 0.8,
            "Model C": {"mean": 0.7, "std": 0.1}
        }
    }
    assert get_best_model_name(results_mock) == "Model B"
