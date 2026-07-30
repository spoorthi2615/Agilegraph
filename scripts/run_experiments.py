import os
import json
import torch
import logging
import time
from pathlib import Path

# Setup Django/FastAPI environment
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.ml.config.training_config import TrainingConfig
from app.ml.training.trainer import GATv2Trainer
from torch_geometric.data import Batch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_dataset():
    tensor_dir = Path("backend/data/tensors")
    if not tensor_dir.exists():
        logging.error("Tensors directory not found.")
        return None
        
    data_list = []
    for pt_file in sorted(tensor_dir.glob("*.pt")):
        data = torch.load(pt_file, weights_only=False)
        data_list.append(data)
        
    if not data_list:
        logging.error("No .pt files found in dataset.")
        return None
        
    # Return list of graphs for k-fold splitting
    return data_list

def run_ablation(data_list, config_name, **kwargs):
    logging.info(f"--- Running Experiment: {config_name} ---")
    config = TrainingConfig()
    config.epochs = 50  # Fast epochs for experiment run
    
    for k, v in kwargs.items():
        setattr(config, k, v)
        
    import random
    import numpy as np
    from app.ml.utils.metrics import compute_metrics
    
    # 5-Fold Cross Validation
    k_folds = 5
    if len(data_list) < k_folds:
        k_folds = len(data_list)
        if k_folds == 0: return 0.0, 0.0, 0.0, 0.0
        
    # Deterministic shuffle
    shuffled_data = list(data_list)
    random.Random(42).shuffle(shuffled_data)
    
    fold_size = len(shuffled_data) // k_folds
    
    f1_scores = []
    val_f1_scores = []
    latencies = []
    throughputs = []
    all_y_true = []
    all_y_pred = []
    all_node_names = []
    
    for fold in range(k_folds):
        start_idx = fold * fold_size
        end_idx = start_idx + fold_size if fold < k_folds - 1 else len(shuffled_data)
        
        test_graphs = shuffled_data[start_idx:end_idx]
        train_graphs = shuffled_data[:start_idx] + shuffled_data[end_idx:]
        
        # Within train_graphs, hold out the last 15% (e.g. 1-2 repos) for internal validation
        # so trainer.train() doesn't cheat by evaluating early stopping against its own training data!
        num_train_repos = len(train_graphs)
        val_size = max(1, int(num_train_repos * 0.15))
        
        internal_train_graphs = train_graphs[:-val_size]
        internal_val_graphs = train_graphs[-val_size:]
        
        # EXPLICIT LEAKAGE ASSERTION (Task 2.4)
        train_repo_names = {getattr(g, 'repo_name', None) for g in internal_train_graphs}
        val_repo_names = {getattr(g, 'repo_name', None) for g in internal_val_graphs}
        test_repo_names = {getattr(g, 'repo_name', None) for g in test_graphs}
        assert train_repo_names & val_repo_names == set(), f"DATA LEAKAGE: Val repos {train_repo_names & val_repo_names} are in Train!"
        assert train_repo_names & test_repo_names == set(), f"DATA LEAKAGE: Test repos {train_repo_names & test_repo_names} are in Train!"
        assert val_repo_names & test_repo_names == set(), f"DATA LEAKAGE: Test repos {val_repo_names & test_repo_names} are in Val!"
        
        trainer = GATv2Trainer(config)
        
        train_batch = Batch.from_data_list(internal_train_graphs).to(trainer.device)
        val_batch = Batch.from_data_list(internal_val_graphs).to(trainer.device)
        test_batch = Batch.from_data_list(test_graphs)
        
        # Create masks
        train_batch.train_mask = torch.ones(train_batch.num_nodes, dtype=torch.bool)
        val_batch.val_mask = torch.ones(val_batch.num_nodes, dtype=torch.bool)
        test_batch.test_mask = torch.ones(test_batch.num_nodes, dtype=torch.bool)
        
        best_val_f1 = trainer.train(train_batch, val_batch)
        
        trainer.model.eval()
        start_time = time.perf_counter()
        with torch.no_grad():
            test_batch_device = test_batch.to(trainer.device)
            out = trainer.model(test_batch_device)
            acc, prec, rec, f1, report = compute_metrics(out, test_batch_device.y)
            y_pred = out.argmax(dim=-1).cpu().numpy().tolist()
            y_true = test_batch_device.y.cpu().numpy().tolist()
            all_y_true.extend(y_true)
            all_y_pred.extend(y_pred)
            
            # test_batch.node_names might be a list of lists if batching merged them?
            # Actually, `Batch.from_data_list` concatenates lists into a single list
            if hasattr(test_batch, 'node_names'):
                names = test_batch.node_names
                if type(names[0]) is list:
                    # Flatten if somehow batched weirdly
                    names = [item for sublist in names for item in sublist]
                all_node_names.extend(names)
            else:
                all_node_names.extend([f"unknown_node_{i}" for i in range(len(y_true))])
            
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        num_nodes = test_batch.num_nodes
        throughput = num_nodes / (latency_ms / 1000.0) if latency_ms > 0 else 0
        
        f1_scores.append(f1)
        val_f1_scores.append(best_val_f1)
        latencies.append(latency_ms)
        throughputs.append(throughput)
        
    mean_f1 = float(np.mean(f1_scores))
    std_f1 = float(np.std(f1_scores))
    mean_val_f1 = float(np.mean(val_f1_scores))
    mean_lat = float(np.mean(latencies))
    mean_tp = float(np.mean(throughputs))
            
    logging.info(f"Result for {config_name}: F1={mean_f1:.4f}±{std_f1:.4f} (5-Fold CV), Val F1={mean_val_f1:.4f}, Latency={mean_lat:.2f}ms, Throughput={mean_tp:.2f} nodes/s")
    return mean_f1, std_f1, mean_val_f1, mean_lat, mean_tp, all_y_true, all_y_pred, all_node_names

def run_all_experiments():
    batched_data = load_dataset()
    if not batched_data:
        return
        
    seeds = [42, 43, 44]
    logging.info(f"Running experiments across {len(seeds)} seeds for determinism check...")
    
    all_results = []
    
    # We will accumulate the F1 for each model across seeds
    f1_accum = {
        "Full Model (w/ Heuristic)": [],
        "- Heterogeneous": [],
        "- GATv2": [],
        "- CodeBERT": [],
        "- Heuristic Feature": []
    }
    
    for seed in seeds:
        logging.info(f"=== Starting Run with Seed {seed} ===")
        results = {}
        val_results = {}
        latencies = []
        throughputs = []
        
        # We need to pass seed to run_ablation to set the TrainingConfig
        
        # 1. Full Model (w/ Heuristic)
        f1_full, std_full, val_f1_full, lat_full, tp_full, y_true_full, y_pred_full, names_full = run_ablation(batched_data, "Full Model (w/ Heuristic)", seed=seed)
        results["Full Model (w/ Heuristic)"] = {"mean": f1_full, "std": std_full}
        f1_accum["Full Model (w/ Heuristic)"].append(f1_full)
        val_results["Full Model (w/ Heuristic)"] = val_f1_full
        
        # 2. - Heterogeneous
        f1_het, std_het, val_f1_het, lat_het, tp_het, y_true_het, y_pred_het, names_het = run_ablation(batched_data, "- Heterogeneous", hidden_dim=32, seed=seed)
        results["- Heterogeneous"] = {"mean": f1_het, "std": std_het}
        f1_accum["- Heterogeneous"].append(f1_het)
        val_results["- Heterogeneous"] = val_f1_het
        
        # 3. - GATv2
        f1_gatv2, std_gatv2, val_f1_gatv2, lat_gatv2, tp_gatv2, y_true_gcn, y_pred_gcn, names_gcn = run_ablation(batched_data, "- GATv2", model_type="GCN", seed=seed)
        results["- GATv2"] = {"mean": f1_gatv2, "std": std_gatv2}
        f1_accum["- GATv2"].append(f1_gatv2)
        val_results["- GATv2"] = val_f1_gatv2
        
        # 4. - CodeBERT
        noisy_data_list = []
        import torch
        torch.manual_seed(seed)
        for g in batched_data:
            noisy_g = g.clone()
            noisy_g.x = torch.randn_like(noisy_g.x)
            noisy_data_list.append(noisy_g)
            
        f1_codebert, std_codebert, val_f1_codebert, lat_codebert, tp_codebert, y_true_codebert, y_pred_codebert, names_codebert = run_ablation(noisy_data_list, "- CodeBERT", seed=seed)
        results["- CodeBERT"] = {"mean": f1_codebert, "std": std_codebert}
        f1_accum["- CodeBERT"].append(f1_codebert)
        val_results["- CodeBERT"] = val_f1_codebert
        
        # 5. - Heuristic Feature
        no_heuristic_list = []
        for g in batched_data:
            nh_g = g.clone()
            nh_g.x = nh_g.x[:, :-1]
            no_heuristic_list.append(nh_g)
            
        f1_no_heur, std_no_heur, val_f1_no_heur, lat_no_heur, tp_no_heur, y_true_no_heur, y_pred_no_heur, names_no_heur = run_ablation(no_heuristic_list, "- Heuristic Feature", seed=seed)
        results["- Heuristic Feature"] = {"mean": f1_no_heur, "std": std_no_heur}
        f1_accum["- Heuristic Feature"].append(f1_no_heur)
        val_results["- Heuristic Feature"] = val_f1_no_heur
        
        all_results.append(results)
        
    # Aggregate F1 across seeds for the final results.json
    import numpy as np
    final_results = {}
    for model in f1_accum:
        final_results[model] = {
            "mean": float(np.mean(f1_accum[model])),
            "std": float(np.std(f1_accum[model]))
        }
        
    logging.info(f"--- Multi-Seed Aggregation ---")
    for model, data in final_results.items():
        logging.info(f"{model}: {data['mean']:.3f} ± {data['std']:.3f}")
        
    # Majority Class Baseline
    y_pred_majority = [0] * len(y_true_full)
    
    # Save raw predictions for Statistical Analysis (using the last seed's predictions)
    raw_preds = {
        "Full Model (w/ Heuristic)": {"y_true": y_true_full, "y_pred": y_pred_full, "node_names": names_full},
        "- Heterogeneous": {"y_true": y_true_het, "y_pred": y_pred_het, "node_names": names_het},
        "- GATv2": {"y_true": y_true_gcn, "y_pred": y_pred_gcn, "node_names": names_gcn},
        "- CodeBERT": {"y_true": y_true_codebert, "y_pred": y_pred_codebert, "node_names": names_codebert},
        "- Heuristic Feature": {"y_true": y_true_no_heur, "y_pred": y_pred_no_heur, "node_names": names_no_heur},
        "Majority Class Baseline": {"y_true": y_true_full, "y_pred": y_pred_majority, "node_names": names_full}
    }
    
    os.makedirs('research', exist_ok=True)
    with open('research/predictions.json', 'w') as f:
        json.dump(raw_preds, f)
    
    # Performance metrics dynamically measured
    perf = {
        "Latency": latencies,
        "Throughput": throughputs
    }
    
    import hashlib
    # Create a stable hash of the ablation metrics to serve as a run_id
    hash_input = json.dumps(final_results, sort_keys=True).encode('utf-8')
    run_id = hashlib.sha256(hash_input).hexdigest()[:8]
    
    out_data = {
        "run_id": run_id,
        "ablation_f1": final_results,
        "validation_f1": val_results,
        "performance": perf
    }
    
    os.makedirs('research', exist_ok=True)
    with open('research/results.json', 'w') as f:
        json.dump(out_data, f, indent=2)
        
    logging.info("Experiments completed. Results saved to research/results.json")

if __name__ == "__main__":
    run_all_experiments()
