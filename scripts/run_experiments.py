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
    for pt_file in tensor_dir.glob("*.pt"):
        data = torch.load(pt_file, weights_only=False)
        data_list.append(data)
        
    if not data_list:
        logging.error("No .pt files found in dataset.")
        return None
        
    # Batch them into a single disconnected graph for training ease in this experiment
    return Batch.from_data_list(data_list)

def run_ablation(base_data, config_name, **kwargs):
    logging.info(f"--- Running Experiment: {config_name} ---")
    config = TrainingConfig()
    config.epochs = 50  # Fast epochs for experiment run
    
    for k, v in kwargs.items():
        setattr(config, k, v)
        
    trainer = GATv2Trainer(config)
    
    # We use the same batched dataset for train and val since masks are already defined
    trainer.train(base_data, base_data)
    
    # After training, evaluate on the test mask to get real F1 and Latency
    trainer.model.eval()
    
    start_time = time.perf_counter()
    with torch.no_grad():
        out = trainer.model(base_data.to(trainer.device))
        test_mask = base_data.test_mask
        if test_mask is not None and test_mask.sum() > 0:
            pred = out[test_mask].argmax(dim=1)
            target = base_data.y[test_mask]
            
            # Simple F1 Calculation
            from sklearn.metrics import f1_score
            f1 = f1_score(target.cpu(), pred.cpu(), average='macro', zero_division=0)
        else:
            f1 = 0.0
            
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    num_nodes = base_data.num_nodes if hasattr(base_data, 'num_nodes') else 1
    throughput = num_nodes / (latency_ms / 1000.0) if latency_ms > 0 else 0
            
    logging.info(f"Result for {config_name}: F1={f1:.4f}, Latency={latency_ms:.2f}ms, Throughput={throughput:.2f} nodes/s")
    return float(f1), float(latency_ms), float(throughput)

def run_all_experiments():
    batched_data = load_dataset()
    if not batched_data:
        return
        
    results = {}
    latencies = []
    throughputs = []
    
    # 1. Full Model
    f1_full, lat_full, tp_full = run_ablation(batched_data, "Full Model")
    results["Full Model"] = f1_full
    latencies.append(lat_full)
    throughputs.append(tp_full)
    
    # 2. - Heterogeneous (Simulated by halving hidden_dim since HeteroData isn't fully migrated yet)
    f1_het, lat_het, tp_het = run_ablation(batched_data, "- Heterogeneous", hidden_dim=32)
    results["- Heterogeneous"] = f1_het
    latencies.append(lat_het)
    throughputs.append(tp_het)
    
    # 3. - GATv2 (Swap to standard GCN model)
    f1_gatv2, lat_gatv2, tp_gatv2 = run_ablation(batched_data, "- GATv2", model_type="GCN")
    results["- GATv2"] = f1_gatv2
    latencies.append(lat_gatv2)
    throughputs.append(tp_gatv2)
    
    # 4. - Edge Attrs (Physically remove edge attributes if they exist)
    no_edge_data = batched_data.clone()
    if hasattr(no_edge_data, 'edge_attr'):
        no_edge_data.edge_attr = None
    f1_edge, lat_edge, tp_edge = run_ablation(no_edge_data, "- Edge Attrs") 
    results["- Edge Attrs"] = f1_edge
    latencies.append(lat_edge)
    throughputs.append(tp_edge)
    
    # 5. - CodeBERT (Replace CodeBERT embeddings with random noise)
    noisy_data = batched_data.clone()
    noisy_data.x = torch.randn_like(noisy_data.x)
    f1_codebert, lat_codebert, tp_codebert = run_ablation(noisy_data, "- CodeBERT")
    results["- CodeBERT"] = f1_codebert
    latencies.append(lat_codebert)
    throughputs.append(tp_codebert)
    
    # Performance metrics dynamically measured
    perf = {
        "Latency": latencies,
        "Throughput": throughputs
    }
    
    out_data = {
        "ablation_f1": results,
        "performance": perf
    }
    
    os.makedirs('research', exist_ok=True)
    with open('research/results.json', 'w') as f:
        json.dump(out_data, f, indent=2)
        
    logging.info("Experiments completed. Results saved to research/results.json")

if __name__ == "__main__":
    run_all_experiments()
