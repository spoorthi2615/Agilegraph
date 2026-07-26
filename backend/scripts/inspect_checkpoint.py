import torch
import os

def inspect():
    path = "backend/outputs/models/gatv2_best.pt"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    try:
        # Load without weights_only first just to see exactly what is inside
        ckpt = torch.load(path, map_location="cpu", weights_only=False)
        print("--- CHECKPOINT KEYS ---")
        if isinstance(ckpt, dict):
            for k, v in ckpt.items():
                print(f"Key: {k}, Type: {type(v)}")
                if k == 'architecture':
                    print(f"  -> Architecture data: {v}")
        else:
            print(f"Checkpoint is not a dict, type: {type(ckpt)}")
            
        # Also try loading with weights_only=True to see if it blocks 'architecture'
        try:
            ckpt_safe = torch.load(path, map_location="cpu", weights_only=True)
            print("\n--- WEIGHTS_ONLY=TRUE CHECKPOINT KEYS ---")
            for k, v in ckpt_safe.items():
                print(f"Key: {k}")
        except Exception as e:
            print(f"Failed to load with weights_only=True: {e}")
            
    except Exception as e:
        print(f"Error loading checkpoint: {e}")

if __name__ == "__main__":
    inspect()
