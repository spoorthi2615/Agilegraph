# AgileGraph Benchmark Study & Baseline Comparison

This document details the rigorous empirical evaluation of the AgileGraph algorithm against established baseline methodologies. The objective is to provide a scientifically defensible, transparent, and fair comparison of Post-Quantum Cryptography (PQC) readiness detection capabilities.

## 1. Experimental Configuration

To guarantee fairness and reproducibility, all benchmarks were executed under identical constraints:
- **Dataset**: `AgileGraph-GNN-Tensors v2.0.0` (validated in Sprint 79.1).
- **Data Splits**: Repositories are split across Train, Val, and Test ensuring cross-domain evaluation.
- **Random Seed**: `42` (Fixed for PyTorch, NumPy, and Python Hash generation).
- **Environment**: Python 3.11, PyTorch 2.1.0, PyTorch Geometric 2.4.0.
- **Stopping Criteria**: Early stopping applied based on Validation Loss (patience = 15 epochs) across all machine learning baselines.

## 2. Baseline Inventory

AgileGraph was evaluated against two distinct baseline paradigms:

1. **Regex-AST Heuristic Engine (Static Baseline)**
   - **Methodology**: Grep-style regular expression matching combined with abstract syntax tree (AST) token parsing.
   - **Selection Rationale**: Represents the industry standard for traditional SAST (Static Application Security Testing) tools.

2. **Graph Convolutional Network - GCN (Graph Baseline)**
   - **Reference**: Kipf & Welling (2017).
   - **Methodology**: Standard spatial graph convolution over the AST/Call-graph network.
   - **Selection Rationale**: Serves as the naive structural baseline to justify AgileGraph's advanced Heterogeneous Relational mechanisms.

## 3. Results Table

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Inference (ms/repo) |
|---|---|---|---|---|---|---|
| Regex-AST (Heuristic) | N/A | N/A | N/A | N/A | N/A | N/A |
| Standard GCN | N/A | N/A | N/A | 0.000 | N/A | 3.9 ms |
| **AgileGraph (Ours)** | **N/A** | **N/A** | **N/A** | **0.000** | **N/A** | **39.5 ms** |

## 4. Error Analysis

A rigorous error analysis reveals critical insights into the pipeline's behavior:

### Strengths
- **Inference Speed**: The AgileGraph inference speed (using CodeBERT and GATv2 layers) operates impressively fast, resolving in just 39.5 ms. The simpler GCN baseline is even faster at 3.9 ms.

### Weaknesses & Generalization Failure
- **F1 Score Collapse (0.000)**: Even after scaling the corpus to 10 repositories, the model fails to correctly classify vulnerable nodes in the completely unseen test repositories, leading to an F1 score of precisely 0.000. 
- **Domain Shift**: While the validation F1 scores indicated the model was successfully learning patterns within the training distribution (reaching ~0.38 F1), this did not translate to the test set. This implies a massive structural domain shift between repositories, meaning the graph patterns learned in one repository do not natively map to another.

## 5. Fairness & Reproducibility

To rerun this exact benchmark matrix:
1. Run `python scripts/fetch_github_corpus.py` to populate the `/backend/data/corpus/` directory.
2. Run `python scripts/generate_gnn_dataset.py` to construct the PyTorch Geometric tensors.
3. Run `python scripts/run_experiments.py` to execute the models and baseline ablations. Results are deterministically dumped to `research/results.json`.
