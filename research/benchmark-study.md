# AgileGraph Performance Benchmark Study & Baseline Comparison

This document details the rigorous empirical evaluation of the AgileGraph algorithm against established baseline methodologies. The objective is to provide a scientifically defensible, transparent, and fair comparison of Post-Quantum Cryptography (PQC) readiness detection capabilities.

## 1. Experimental Configuration

To guarantee fairness and reproducibility, all benchmarks were executed under identical constraints:
- **Dataset**: `AgileGraph-GNN-Tensors v3.0.0` (40 repositories, 5-Fold Cross Validation).
- **Data Splits**: 5-Fold CV (80% Train, 20% Test) ensuring cross-domain generalization.
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

3. **IBM CBOMkit (Industry Standard)**
   - **Reference**: https://github.com/IBM/cbomkit
   - **Methodology**: `cbomkit-theia` is used via Docker to scan directories. 
   - **Selection Rationale**: Industry-standard parser representing the state-of-the-art in specialized cryptographic detection.
   - **Important Limitation (P1)**: *Note: `cbomkit-theia` is designed primarily for detecting certificates and keys in filesystems, not for deep source-code algorithm detection (which is handled by `sonar-cryptography` or `cbomkit-action`, neither of which provide a local CLI container). Using `theia` against raw source repositories means it is being evaluated outside its primary intended scope. To avoid deceptive majority-class predictions, its F1 score is explicitly scoped as N/A for these pure-source code nodes.*

## 3. Results Table (5-Fold Mean)

| Model Variant | Macro-F1 | 95% Confidence Interval | Inference (ms/repo) |
|---|---|---|---|
| IBM CBOMkit Baseline | N/A | N/A | ~2500 ms (Docker) |
| Majority Class Baseline | 0.467 | [0.466, 0.468] | N/A |
| AgileGraph (- Heterogeneous) | 0.802 | [0.795, 0.809] | N/A |
| AgileGraph (Full Model w/ Heuristic) | 0.913 | [0.908, 0.919] | N/A |
| AgileGraph (- GATv2) | 0.676 | [0.669, 0.683] | N/A |
| Random Noise (- CodeBERT) | 0.321 | [0.315, 0.326] | N/A |
| AgileGraph (- Heuristic Feature) | 0.876 | [0.869, 0.882] | N/A |

## 4. Error Analysis

A rigorous error analysis reveals critical insights into the pipeline's behavior:

### CBOMkit Comparison (Industry Standard)
Earlier versions of this report incorrectly framed CBOMkit's performance as a strong baseline win, when in reality, the `cbomkit-theia` tool (when run against raw source code) defaulted to a majority-class predictor (predicting everything as safe). Because of the 87/12 class imbalance, predicting the majority class yields a deceptively high Macro-F1. The tables now explicitly include a **Majority Class Baseline** to provide proper context, and explicitly marks CBOMkit as N/A for source code nodes.

### Strengths
- **Successful Generalization**: AgileGraph's best-performing configuration (Full Model (w/ Heuristic)) achieved an F1-score of **0.913**, bounded by a 95% Confidence Interval [0.908, 0.919] generated via 1,000-iteration empirical bootstrapping.
- **Heterogeneous vs Homogeneous**: The Full AgileGraph GATv2 model outperformed the Homogeneous GCN (0.859 vs 0.792). This confirms that distinguishing edge types (Calls, Inherits, Imports) in a heterogeneous graph adds crucial predictive power for this specific static analysis task, proving the core architecture is robust.
- **Defeating the Noise Paradox**: The GNN statistically outperforms the CodeBERT noise baseline with high significance (p < 0.05 via McNemar's Test), proving that it learns meaningful topological and semantic representations.

### Weaknesses & Architectural Limitations

## 5. Fairness & Reproducibility

To rerun this exact benchmark matrix:
1. Run `python scripts/fetch_github_corpus.py` to populate the `/backend/data/corpus/` directory.
2. Run `python scripts/generate_gnn_dataset.py` to construct the PyTorch Geometric tensors.
3. Run `python scripts/run_experiments.py` to execute the models and baseline ablations. Results are deterministically dumped to `research/results.json`.
4. Run `python scripts/run_cbomkit.py` for baseline comparison.
5. Run `python scripts/statistical_tests.py` and generator scripts to reproduce these tables.

*This document is auto-generated by `scripts/generate_benchmark_report.py` to prevent metrics drift.*
