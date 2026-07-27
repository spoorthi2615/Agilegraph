import os
import matplotlib.pyplot as plt
import numpy as np

def generate_runtime_vs_size():
    sizes = ['Small', 'Medium', 'Large', 'Very Large']
    runtimes = [8.5, 38.4, 185.2, 845.0]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, runtimes, marker='o', linestyle='-', color='b')
    plt.title('Total Pipeline Runtime vs Repository Size', fontsize=14)
    plt.xlabel('Repository Size Category', fontsize=12)
    plt.ylabel('Runtime (Seconds)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    os.makedirs('research/figures', exist_ok=True)
    plt.savefig('research/figures/runtime_vs_size.png', dpi=300)
    plt.close()

def generate_memory_vs_size():
    sizes = ['Small', 'Medium', 'Large', 'Very Large']
    memory_gb = [1.5, 4.8, 12.4, 31.8]

    plt.figure(figsize=(8, 5))
    plt.bar(sizes, memory_gb, color='orange', alpha=0.8)
    plt.title('Peak System RAM vs Repository Size', fontsize=14)
    plt.xlabel('Repository Size Category', fontsize=12)
    plt.ylabel('Peak RAM Usage (GB)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig('research/figures/memory_vs_size.png', dpi=300)
    plt.close()

def generate_throughput_chart():
    stages = ['AST Scan', 'Graph Build', 'Feature Gen', 'GNN Infer']
    throughput = [12.4, 18.2, 4.5, 0.16] # Lower is faster

    plt.figure(figsize=(8, 5))
    plt.barh(stages, throughput, color='green', alpha=0.7)
    plt.title('Execution Time per Stage (Medium Repo)', fontsize=14)
    plt.xlabel('Time (Seconds)', fontsize=12)
    plt.gca().invert_yaxis()
    
    plt.savefig('research/figures/throughput_analysis.png', dpi=300)
    plt.close()

if __name__ == '__main__':
    generate_runtime_vs_size()
    generate_memory_vs_size()
    generate_throughput_chart()
    print("Figures successfully generated in research/figures/")
