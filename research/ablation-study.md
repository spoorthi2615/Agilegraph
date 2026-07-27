# Ablation Study & Component Contribution Analysis

This document details a strict ablation study designed to isolate and quantify the individual performance contribution of every major architectural component within the AgileGraph Post-Quantum Cryptography prediction pipeline. 

## 1. Experimental Design & Consistency
To maintain absolute isolation, the study adheres to a single-component removal methodology. Each experiment selectively disables exactly one feature block while leaving all other elements (Dataset splits, Random Seed=42, Loss function, Early Stopping) completely unchanged from the Full Model baseline.

### Ablated Variants
- **Full AgileGraph**: The complete production architecture.
- **- w/o Heterogeneous Edges**: Flattens the graph into a homogeneous structure (all edges treated as standard connections rather than distinguishing between `CALLS`, `IMPORTS`, `INHERITS`).
- **- w/o GATv2 Attention**: Replaces the dynamic GATv2 attention heads with static GraphSAGE mean aggregation.
- **- w/o Heuristic Edge Attributes**: Removes semantic edge weights (e.g., token distance, block scoping).
- **- w/o CodeBERT Embeddings**: Replaces the contextual NLP node embeddings with standard bag-of-words (BoW) tf-idf vectors.

## 2. Contribution Analysis Results

| Model Variant | F1-Score | Diff vs Full | Recall | Runtime (ms) |
|---|---|---|---|---|
| **Full AgileGraph** | **0.000** | - | **0.000** | 39.5 |
| - w/o Heterogeneous Edges | 0.000 | 0.000 | 0.000 | 22.6 |
| - w/o GATv2 Attention (GCN) | 0.000 | 0.000 | 0.000 | **3.9** |
| - w/o CodeBERT Features | 0.380 | +0.380 | 0.000 | 31.4 |

## 3. Interpretation & Component Ranking

- **The Noise-Substitution Paradox (CodeBERT Ablation)**: The most critical and concerning finding of this study is that the highest validation F1 score (0.380) occurred in the `- CodeBERT` arm, where semantic CodeBERT embeddings were entirely replaced with `torch.randn_like()` random noise. The fact that random noise outperformed real CodeBERT embeddings on the validation set strongly suggests that the model is completely ignoring code semantics. Instead, it is likely finding shortcuts by overfitting to graph structure (e.g., node degrees) or class imbalances in the tiny validation set.
- **Zero-Shot Generalization Failure**: The test set F1-score remains identically 0.000 across all configurations. The graph structures and features learned on the training repositories do not meaningfully transfer to unseen repositories, indicating a severe domain shift problem that the current GNN architecture fails to bridge.
- **Note on Edge Attributes**: An earlier iteration of this study included an "- Edge Attrs" ablation arm. This arm was removed after log inspection revealed it produced byte-identical epoch outputs to the Full Model. The `GATv2Model` does not actually process `edge_attr` tensors in its forward pass, so removing them had no physical effect on the network.
- Dropping Heterogeneous edges also yields a massive runtime acceleration (22.6 ms) because heterogeneous message passing dictates multiple independent weight matrices.

## 4. Threats to Validity & Unexpected Observations
**Threat to Validity**: The ablation study currently only disables components independently. It does not measure higher-order interaction effects (e.g., removing *both* GATv2 and Heterogeneous edges simultaneously), which might trigger non-linear performance decay. Future factorial design studies are recommended.
