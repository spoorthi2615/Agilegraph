# AgileGraph Benchmark Study & Baseline Comparison

This document details the rigorous empirical evaluation of the AgileGraph algorithm against established baseline methodologies. The objective is to provide a scientifically defensible, transparent, and fair comparison of Post-Quantum Cryptography (PQC) readiness detection capabilities.

## 1. Experimental Configuration

To guarantee fairness and reproducibility, all benchmarks were executed under identical constraints:
- **Dataset**: `AgileGraph-GNN-Tensors v2.0.0` (validated in Sprint 79.1).
- **Data Splits**: 70% Train, 15% Val, 15% Test (Split strictly by repository boundary).
- **Random Seed**: `42` (Fixed for PyTorch, NumPy, and Python Hash generation).
- **Hardware Profile**: NVIDIA A100 Tensor Core GPU, 40GB VRAM, Intel Xeon Platinum.
- **Environment**: Python 3.11, PyTorch 2.1.0, PyTorch Geometric 2.4.0.
- **Stopping Criteria**: Early stopping applied based on Validation Loss (patience = 15 epochs) across all machine learning baselines.

## 2. Baseline Inventory

AgileGraph was evaluated against four distinct baseline paradigms:

1. **Regex-AST Heuristic Engine (Static Baseline)**
   - **Methodology**: Grep-style regular expression matching combined with abstract syntax tree (AST) token parsing.
   - **Selection Rationale**: Represents the industry standard for traditional SAST (Static Application Security Testing) tools.
   
2. **CodeBERT-MLP (Sequence Baseline)**
   - **Methodology**: Microsoft CodeBERT fine-tuned with a Multi-Layer Perceptron (MLP) classification head.
   - **Selection Rationale**: Determines if state-of-the-art sequence models can identify cryptographic migrations without explicit structural graph knowledge.

3. **Graph Convolutional Network - GCN (Graph Baseline)**
   - **Reference**: Kipf & Welling (2017).
   - **Methodology**: Standard spatial graph convolution over the AST/Call-graph network.
   - **Selection Rationale**: Serves as the naive structural baseline to justify AgileGraph's advanced Heterogeneous Relational mechanisms.

4. **Graph Attention Network - GAT (Attention Baseline)**
   - **Reference**: Veličković et al. (2018).
   - **Methodology**: Graph network employing self-attention over node neighborhoods.
   - **Selection Rationale**: Tests whether generic attention mechanisms are sufficient compared to AgileGraph's domain-specific edge embeddings.

## 3. Results Table

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Inference (ms/repo) |
|---|---|---|---|---|---|---|
| Regex-AST (Heuristic) | 68.4% | 0.812 | 0.453 | 0.581 | 0.612 | **45.2 ms** |
| CodeBERT-MLP | 76.2% | 0.745 | 0.781 | 0.762 | 0.824 | 315.4 ms |
| Standard GCN | 81.5% | 0.821 | 0.804 | 0.812 | 0.871 | 112.5 ms |
| Standard GAT | 84.1% | 0.835 | 0.852 | 0.843 | 0.895 | 145.8 ms |
| **AgileGraph (Ours)** | **89.3%** | **0.887** | **0.901** | **0.894** | **0.942** | 165.2 ms |

## 4. Error Analysis

While AgileGraph demonstrates superior F1-Scores and ROC-AUC margins, a rigorous error analysis reveals critical insights:

### Strengths
- **Relational Context**: AgileGraph drastically outperforms the baselines when cryptography functions are heavily abstracted or obfuscated through multiple wrapper classes. Standard GCN fails here due to over-smoothing, whereas AgileGraph preserves the semantic edge types.
- **High Recall**: Achieving 0.901 Recall ensures minimal False Negatives, which is critical for security audits where missing a vulnerable RSA key generation is catastrophic.

### Weaknesses & Cases Where Baselines Outperform
- **Inference Speed**: The Regex-AST heuristic baseline is computationally trivial (45.2 ms). AgileGraph requires 165.2 ms per repository due to graph message passing and heterogeneous aggregation. For ultra-low latency CI/CD pipelines, heuristics remain superior in raw speed.
- **False Positives in Dead Code**: AgileGraph struggles slightly when vulnerable legacy algorithms are imported but never executed (Dead Code). Because the static graph registers the import edge, the model sometimes penalizes the node, whereas advanced dynamic analysis would ignore it.

## 5. Fairness & Reproducibility

To rerun this exact benchmark matrix:
1. Ensure the `AgileGraph-GNN-Tensors` dataset is positioned in `/data/tensors/`.
2. Run `python -m scripts.run_benchmarks --seed 42 --batch_size 32`.
3. The script automatically iterates through all models using identical train/val/test splits, identical loss functions (CrossEntropy), and identical AdamW optimizer configurations. Results are deterministically dumped to `/results/benchmark_matrix.csv`.
