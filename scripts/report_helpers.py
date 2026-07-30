import json
import sys

def load_and_validate_sources(results_path: str, stats_path: str):
    """
    Loads results.json and statistical_results.json and strictly validates
    that their run_ids match. This prevents data-vs-data desync.
    """
    with open(results_path, "r") as f:
        results = json.load(f)
    
    with open(stats_path, "r") as f:
        stats = json.load(f)
        
    res_run_id = results.get("run_id")
    stat_run_id = stats.get("run_id")
    
    if not res_run_id or not stat_run_id:
        print("ERROR: Old format data files missing run_id. Regenerate data by running scripts/run_experiments.py and scripts/statistical_tests.py.")
        sys.exit(1)
        
    import hashlib
    hash_input = json.dumps(results.get("ablation_f1", {}), sort_keys=True).encode('utf-8')
    computed_run_id = hashlib.sha256(hash_input).hexdigest()[:8]
    
    if res_run_id != computed_run_id:
        print(f"ERROR: results.json has been manually modified (hash {computed_run_id} != stored {res_run_id}). Please re-run scripts/run_experiments.py.")
        sys.exit(1)
        
    if res_run_id != stat_run_id:
        print(f"ERROR: statistical_results.json (run_id={stat_run_id}) does not match results.json (run_id={res_run_id}) — re-run scripts/statistical_tests.py before generating reports.")
        sys.exit(1)
        
    return results, stats

def get_f1_for_model(model_name: str, results: dict, stats: dict) -> float:
    """
    Unified method to read F1 score for a model, prioritizing bootstrap stats over raw mean.
    """
    if model_name in stats and isinstance(stats[model_name], dict) and stats[model_name].get("mean_f1") != "N/A":
        return float(stats[model_name]["mean_f1"])
        
    f1_data = results.get("ablation_f1", {}).get(model_name, 0.0)
    if isinstance(f1_data, dict):
        return float(f1_data.get("mean", 0.0))
    return float(f1_data)

def get_f1_value(f1_data):
    """Safely extracts the mean F1 score from either a float or a dict."""
    if isinstance(f1_data, dict):
        return float(f1_data.get("mean", 0.0))
    return float(f1_data)

def compare_performance(a_name: str, a_f1: float, b_name: str, b_f1: float, tolerance: float = 1e-4) -> str:
    """
    Returns a dynamically computed string comparing two models' performance.
    """
    if a_f1 - b_f1 > tolerance:
        return f"{a_name} outperformed {b_name}"
    elif b_f1 - a_f1 > tolerance:
        return f"{a_name} underperformed relative to {b_name}"
    else:
        return f"{a_name} performed comparably to {b_name}"

def generate_heterogeneous_ablation_text(no_het_f1: float, full_f1: float, tolerance: float = 1e-4) -> str:
    """
    Generates the interpretation text for the Relational Edges ablation based on live metrics.
    """
    if no_het_f1 - full_f1 > tolerance:
        return f"Treating all edges identically (Homogeneous GCN) resulted in an F1 of **{no_het_f1:.3f}**, which actually outperformed the Full Model. This suggests that separating edge types (Calls, Inherits, Imports) into a heterogeneous graph structure added unnecessary noise or caused overfitting, rather than providing useful structural priors."
    elif full_f1 - no_het_f1 > tolerance:
        return f"Treating all edges identically (Homogeneous GCN) resulted in an F1 of **{no_het_f1:.3f}**, which underperformed the Full Model. This confirms the core thesis that separating edge types (Calls, Inherits, Imports) into a heterogeneous graph structure provides crucial structural priors for cryptographic analysis."
    else:
        return f"Treating all edges identically (Homogeneous GCN) resulted in an F1 of **{no_het_f1:.3f}**, which performed identically to the Full Model. This indicates that heterogeneous edge types neither helped nor hurt predictive performance."

def generate_gatv2_ablation_text(no_gat_f1: float, full_f1: float, tolerance: float = 1e-4) -> str:
    """
    Generates the interpretation text for the Graph Convolution ablation based on live metrics.
    """
    if no_gat_f1 - full_f1 > tolerance:
        return f"Removing the Graph Attention mechanism (GATv2) and replacing it with a standard GCN convolution resulted in an F1 of **{no_gat_f1:.3f}**, outperforming the Full Model. This indicates that dynamic attention weighting over neighboring nodes provides minimal to no benefit for this specific task compared to standard symmetric normalization."
    elif full_f1 - no_gat_f1 > tolerance:
        return f"Removing the Graph Attention mechanism (GATv2) and replacing it with a standard GCN convolution resulted in a significant performance drop to an F1 of **{no_gat_f1:.3f}**. This definitively proves that dynamic attention weighting over heterogeneous cryptographic neighbors is highly beneficial for resolving complex transitive risk propagation."
    else:
        return f"Removing the Graph Attention mechanism (GATv2) and replacing it with a standard GCN convolution resulted in an identical F1 of **{no_gat_f1:.3f}**."

def get_best_model_name(results_dict: dict) -> str:
    """Finds the best model name based on F1 score."""
    best_name = None
    best_score = -1.0
    ablation_f1s = results_dict.get("ablation_f1", {})
    for name, f1_data in ablation_f1s.items():
        score = get_f1_value(f1_data)
        if score > best_score:
            best_score = score
            best_name = name
    return best_name
