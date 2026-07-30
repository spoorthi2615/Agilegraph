import torch
from pathlib import Path
from collections import Counter

def inspect_dataset():
    tensor_dir = Path("backend/data/tensors")
    
    if not tensor_dir.exists() or not list(tensor_dir.glob("*.pt")):
        print(f"No tensors found in {tensor_dir}. Please run scripts/generate_gnn_dataset.py first.")
        return
        
    print("="*60)
    print("AGILEGRAPH DATASET DIAGNOSTIC INSPECTION")
    print("="*60)

    total_nodes = 0
    total_edges = 0
    
    split_stats = {
        "train": {"nodes": 0, "labels": []},
        "val": {"nodes": 0, "labels": []},
        "test": {"nodes": 0, "labels": []},
    }
    
    isolated_nodes_total = 0
    
    global_labels = []
    all_x = []

    for pt_file in tensor_dir.glob("*.pt"):
        data = torch.load(pt_file, weights_only=False)
        
        num_nodes = data.num_nodes
        num_edges = data.num_edges
        total_nodes += num_nodes
        total_edges += num_edges
        
        if num_nodes > 0:
            global_labels.extend(data.y.tolist())
            
        all_x.append(data.x)
        
        # Calculate isolated nodes
        if num_edges > 0:
            connected_nodes = torch.unique(data.edge_index)
            isolated_nodes = num_nodes - len(connected_nodes)
        else:
            isolated_nodes = num_nodes
        isolated_nodes_total += isolated_nodes
        
        all_x.append(data.x)
        
        # Determine split from mask
        # Since the generation script assigns entire repos to one split, we can just check the first node
        if num_nodes > 0:
            if hasattr(data, "train_mask") and data.train_mask[0]:
                split = "train"
            elif hasattr(data, "val_mask") and data.val_mask[0]:
                split = "val"
            elif hasattr(data, "test_mask") and data.test_mask[0]:
                split = "test"
            else:
                split = "unknown"
                
            if split in split_stats:
                split_stats[split]["nodes"] += num_nodes
                split_stats[split]["labels"].extend(data.y.tolist())
                
        print(f"Repo: {pt_file.stem:<20} | Nodes: {num_nodes:<5} | Edges: {num_edges:<5} | Split: {split}")

    print("\n" + "="*60)
    print("GLOBAL AGGREGATES")
    print("="*60)
    print(f"Total Repositories: {len(list(tensor_dir.glob('*.pt')))}")
    print(f"Total Nodes: {total_nodes}")
    print(f"Total Edges: {total_edges}")
    print(f"Total Isolated Nodes: {isolated_nodes_total} ({(isolated_nodes_total/total_nodes)*100 if total_nodes > 0 else 0:.2f}%)")
    
    if all_x:
        global_x = torch.cat(all_x, dim=0)
        mean_val = global_x.mean().item()
        std_val = global_x.std().item()
        print(f"Feature (x) Stats   : Mean = {mean_val:.4f}, Std = {std_val:.4f}")

    print("\n" + "="*60)
    print("GLOBAL CLASS DISTRIBUTION")
    print("="*60)
    if total_nodes > 0:
        counts = Counter(global_labels)
        for label, count in counts.items():
            pct = (count / total_nodes) * 100
            print(f"  Class {label}: {count} ({pct:.2f}%)")
    else:
        print("  [WARNING] NO NODES FOUND!")

    print("\n" + "="*60)
    print("SPLIT DISTRIBUTIONS (TRAIN / VAL / TEST)")
    print("="*60)
    
    for split in ["train", "val", "test"]:
        stats = split_stats[split]
        num_nodes = stats["nodes"]
        labels = stats["labels"]
        
        print(f"\n--- {split.upper()} SPLIT ---")
        print(f"Total Nodes: {num_nodes}")
        if num_nodes > 0:
            counts = Counter(labels)
            for label, count in counts.items():
                pct = (count / num_nodes) * 100
                print(f"  Class {label}: {count} ({pct:.2f}%)")
            
            # Check for 100% single class (Degeneracy)
            if len(counts) == 1:
                print(f"  [WARNING] DEGENERATE SPLIT: 100% of nodes are Class {list(counts.keys())[0]}!")
        else:
            print("  [WARNING] SPLIT IS EMPTY!")
            
    print("\n" + "="*60)
    print("Inspection complete.")

if __name__ == "__main__":
    inspect_dataset()
