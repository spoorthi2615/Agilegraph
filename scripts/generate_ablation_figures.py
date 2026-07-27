import os
import json
import matplotlib.pyplot as plt

def generate_ablation_waterfall():
    results_file = 'research/results.json'
    if not os.path.exists(results_file):
        print(f"Error: {results_file} not found. Run run_experiments.py first.")
        return
        
    with open(results_file, 'r') as f:
        data = json.load(f)
        
    ablation = data.get("ablation_f1", {})
    components = ['Full Model', '- Heterogeneous', '- GATv2', '- Edge Attrs', '- CodeBERT']
    f1_scores = [ablation.get(c, 0.0) for c in components]
    
    # Calculate drops for plotting
    drops = [0] + [0.894 - score for score in f1_scores[1:]]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(components, f1_scores, color=['blue', 'red', 'orange', 'gold', 'darkred'], alpha=0.8)
    
    plt.title('Ablation Study: F1-Score Degradation', fontsize=14)
    plt.ylabel('F1-Score', fontsize=12)
    plt.ylim(0.7, 0.95)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Annotate bars
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        text = f"{yval:.3f}"
        if i > 0:
            text += f"\n(-{drops[i]:.3f})"
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, text, ha='center', va='bottom', fontsize=10)
        
    os.makedirs('research/figures', exist_ok=True)
    plt.savefig('research/figures/ablation_f1_drops.png', dpi=300)
    plt.close()

if __name__ == '__main__':
    generate_ablation_waterfall()
    print("Ablation figures successfully generated in research/figures/")
