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
| - w/o Edge Attributes | 0.000 | 0.000 | 0.000 | 31.8 |
| - w/o CodeBERT Features | 0.000 | 0.000 | 0.000 | 31.4 |

## 3. Interpretation & Component Ranking

Because the F1-Score completely collapsed to 0.000 across all permutations even after scaling to 10 repositories, it is mathematically impossible to rank the architectural components by performance contribution based on predictive power.

However, the **Inference Latency** accurately highlights structural overhead:
- Standard GCN (`w/o GATv2`) is incredibly fast (3.9 ms) compared to the Full Model (39.5 ms).
- Dropping Heterogeneous edges also yields a massive runtime acceleration (22.6 ms) because heterogeneous message passing dictates multiple independent weight matrices.

## 4. Threats to Validity & Unexpected Observations
**Threat to Validity**: The ablation study currently only disables components independently. It does not measure higher-order interaction effects (e.g., removing *both* GATv2 and Heterogeneous edges simultaneously), which might trigger non-linear performance decay. Future factorial design studies are recommended.
