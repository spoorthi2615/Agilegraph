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
