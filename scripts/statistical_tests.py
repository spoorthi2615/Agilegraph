import os
import json
import numpy as np
import logging
import sys
from sklearn.metrics import f1_score, precision_score, recall_score
from statsmodels.stats.contingency_tables import mcnemar

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.experiments.cohens_kappa.cohens_kappa_service import CohensKappaService
from app.experiments.cohens_kappa.kappa_config import KappaConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def bootstrap_ci(y_true, y_pred, n_iterations=1000, alpha=0.05):
    """Calculates 95% confidence intervals using empirical bootstrapping."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    f1_scores = []
    
    for _ in range(n_iterations):
        # Sample with replacement
        indices = np.random.choice(len(y_true), len(y_true), replace=True)
        sample_true = y_true[indices]
        sample_pred = y_pred[indices]
        
        # Only compute F1 if there are positive classes in the sample
        if np.sum(sample_true) > 0:
            f1 = f1_score(sample_true, sample_pred, average='macro', zero_division=0)
            f1_scores.append(f1)
            
    if not f1_scores:
        return 0.0, 0.0, 0.0
        
    lower_bound = np.percentile(f1_scores, (alpha / 2.0) * 100)
    upper_bound = np.percentile(f1_scores, (1 - alpha / 2.0) * 100)
    mean_f1 = np.mean(f1_scores)
    
    return mean_f1, lower_bound, upper_bound

def run_mcnemar_test(y_true, y_pred_model_a, y_pred_model_b):
    """
    Runs McNemar's test to compare two models on the same test set.
    Null Hypothesis: The models have the same error rate.
    """
    y_true = np.array(y_true)
    a = np.array(y_pred_model_a)
    b = np.array(y_pred_model_b)
    
    # Correct predictions
    a_correct = (a == y_true)
    b_correct = (b == y_true)
    
    # Contingency table
    # [[Both correct, A correct B wrong],
    #  [A wrong B correct, Both wrong]]
    n00 = np.sum(a_correct & b_correct)
    n01 = np.sum(a_correct & ~b_correct)
    n10 = np.sum(~a_correct & b_correct)
    n11 = np.sum(~a_correct & ~b_correct)
    
    table = [[n00, n01], [n10, n11]]
    result = mcnemar(table, exact=False, correction=True)
    return result.statistic, result.pvalue

def main():
    pred_file = "research/predictions.json"
    if not os.path.exists(pred_file):
        logging.error(f"Cannot find {pred_file}. Run run_experiments.py first.")
        return
        
    with open(pred_file, "r") as f:
        preds = json.load(f)
        
    logging.info("=" * 50)
    logging.info("PHASE 3 STATISTICAL ANALYSIS")
    logging.info("=" * 50)
    
    stats_out = {}
    
    # 1. Bootstrap Confidence Intervals
    for model_name, data in preds.items():
        mean_f1, lb, ub = bootstrap_ci(data["y_true"], data["y_pred"])
        logging.info(f"Model: {model_name}")
        logging.info(f"  Macro-F1 (Bootstrap Mean): {mean_f1:.4f}")
        logging.info(f"  95% CI: [{lb:.4f}, {ub:.4f}]\n")
        
        stats_out[model_name] = {
            "mean_f1": float(mean_f1),
            "ci_lower": float(lb),
            "ci_upper": float(ub)
        }
        
    # 2. McNemar's Test
    # Compare Full Model vs Random Noise (CodeBERT)
    y_true = preds["Full Model"]["y_true"]
    y_full = preds["Full Model"]["y_pred"]
    y_noise = preds["- CodeBERT"]["y_pred"]
    y_het = preds["- Heterogeneous"]["y_pred"]
    
    stat_noise, p_noise = run_mcnemar_test(y_true, y_full, y_noise)
    logging.info(f"McNemar Test: Full Model vs Random Noise (- CodeBERT)")
    logging.info(f"  Statistic: {stat_noise:.4f}, p-value: {p_noise:.4e}")
    if p_noise < 0.05:
        logging.info("  Result: Statistically Significant Difference (p < 0.05)\n")
    else:
        logging.info("  Result: Not Statistically Significant\n")
        
    stat_het, p_het = run_mcnemar_test(y_true, y_full, y_het)
    logging.info(f"McNemar Test: Full Model vs Homogeneous GCN (- Heterogeneous)")
    logging.info(f"  Statistic: {stat_het:.4f}, p-value: {p_het:.4e}")
    if p_het < 0.05:
        logging.info("  Result: Statistically Significant Difference (p < 0.05)\n")
    else:
        logging.info("  Result: Not Statistically Significant\n")
        
    if "CBOMkit Baseline" in preds:
        y_cbom = preds["CBOMkit Baseline"]["y_pred"]
        stat_cbom, p_cbom = run_mcnemar_test(y_true, y_full, y_cbom)
        logging.info(f"McNemar Test: Full Model vs CBOMkit Baseline")
        logging.info(f"  Statistic: {stat_cbom:.4f}, p-value: {p_cbom:.4e}")
        if p_cbom < 0.05:
            logging.info("  Result: Statistically Significant Difference (p < 0.05)\n")
        else:
            logging.info("  Result: Not Statistically Significant\n")
        
        stats_out["mcnemar"] = {
            "full_vs_noise": {"statistic": float(stat_noise), "pvalue": float(p_noise)},
            "full_vs_het": {"statistic": float(stat_het), "pvalue": float(p_het)},
            "full_vs_cbom": {"statistic": float(stat_cbom), "pvalue": float(p_cbom)}
        }
    else:
        stats_out["mcnemar"] = {
            "full_vs_noise": {"statistic": float(stat_noise), "pvalue": float(p_noise)},
            "full_vs_het": {"statistic": float(stat_het), "pvalue": float(p_het)}
        }
        
    # 3. Cohen's Kappa
    kappa_service = CohensKappaService(KappaConfig())
    y_true_str = [str(x) for x in y_true]
    y_full_str = [str(x) for x in y_full]
    
    kappa_res = kappa_service.calculate_kappa("Ground Truth", "Full Model", y_true_str, y_full_str)
    logging.info("Cohen's Kappa: Ground Truth vs Full Model")
    logging.info(f"  Kappa Score: {kappa_res.kappa_score:.4f} ({kappa_res.interpretation})\n")
    
    stats_out["kappa"] = {
        "full_model": {
            "score": float(kappa_res.kappa_score),
            "interpretation": kappa_res.interpretation
        }
    }
    
    if "CBOMkit Baseline" in preds:
        y_cbom_str = [str(x) for x in y_cbom]
        kappa_res_cbom = kappa_service.calculate_kappa("Ground Truth", "CBOMkit Baseline", y_true_str, y_cbom_str)
        logging.info("Cohen's Kappa: Ground Truth vs CBOMkit Baseline")
        logging.info(f"  Kappa Score: {kappa_res_cbom.kappa_score:.4f} ({kappa_res_cbom.interpretation})\n")
        stats_out["kappa"]["cbomkit"] = {
            "score": float(kappa_res_cbom.kappa_score),
            "interpretation": kappa_res_cbom.interpretation
        }
    
    with open("research/statistical_results.json", "w") as f:
        json.dump(stats_out, f, indent=2)

if __name__ == "__main__":
    main()
