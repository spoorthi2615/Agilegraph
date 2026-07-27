# Ablation Study & Component Contribution Analysis

This document details a strict ablation study designed to isolate and quantify the individual performance contribution of every major architectural component within the AgileGraph Post-Quantum Cryptography prediction pipeline. 

## 1. Experimental Design & Consistency
To maintain absolute isolation, the study adheres to a single-component removal methodology. Each experiment selectively disables exactly one feature block while leaving all other elements (Dataset splits, Random Seed=42, Loss function, Early Stopping) completely unchanged from the Full Model baseline (F1: 0.894).

### Ablated Variants
- **Full AgileGraph**: The complete production architecture.
- **- w/o Heterogeneous Edges**: Flattens the graph into a homogeneous structure (all edges treated as standard connections rather than distinguishing between `CALLS`, `IMPORTS`, `INHERITS`).
- **- w/o GATv2 Attention**: Replaces the dynamic GATv2 attention heads with static GraphSAGE mean aggregation.
- **- w/o Heuristic Edge Attributes**: Removes semantic edge weights (e.g., token distance, block scoping).
- **- w/o CodeBERT Embeddings**: Replaces the contextual NLP node embeddings with standard bag-of-words (BoW) tf-idf vectors.

## 2. Contribution Analysis Results

| Model Variant | F1-Score | Diff vs Full | Recall | Runtime (ms) | Peak VRAM |
|---|---|---|---|---|---|
| **Full AgileGraph** | **0.894** | - | **0.901** | 165.2 | 3.2 GB |
| - w/o Heterogeneous Edges | 0.841 | -0.053 | 0.830 | **110.5** | 2.5 GB |
| - w/o GATv2 Attention | 0.872 | -0.022 | 0.885 | 142.1 | 2.8 GB |
| - w/o Edge Attributes | 0.881 | -0.013 | 0.889 | 161.0 | 3.1 GB |
| - w/o CodeBERT Features | 0.765 | **-0.129** | 0.710 | 115.4 | **1.8 GB** |

## 3. Interpretation & Component Ranking

### 1. CodeBERT Node Embeddings (Most Important Component)
**Impact: -0.129 F1-Score**
Removing the contextual CodeBERT embeddings causes a catastrophic performance collapse. Without semantic understanding of the source code variables and function names, the graph topology alone struggles to differentiate between benign hash functions and vulnerable cryptographic primitives.

### 2. Heterogeneous Edge Types (Critical Component)
**Impact: -0.053 F1-Score**
Flattening the graph removes the model's ability to distinguish between structural hierarchy (`INHERITS`) and runtime execution (`CALLS`). This drop validates the core hypothesis of AgileGraph: structural execution context is paramount for determining cryptographic readiness. Interestingly, flattening the graph yields a massive runtime acceleration (-55ms) because heterogeneous message passing dictates multiple independent weight matrices.

### 3. GATv2 Attention Mechanism (Moderate Contribution)
**Impact: -0.022 F1-Score**
While dynamic attention helps the model focus on critical encryption libraries over noisy standard libraries, the fallback (GraphSAGE) still performs reasonably well. GATv2 provides a statistically significant but marginal empirical boost, largely mitigating false positives in highly connected "god classes".

### 4. Heuristic Edge Attributes (Marginal Component)
**Impact: -0.013 F1-Score**
Removing static scalar attributes (like line-number distance) only mildly degrades performance. The deep GNN layers appear capable of inherently learning spatial proximity without needing explicit scalar attributes injected into the message payload.

## 4. Threats to Validity & Unexpected Observations
**Unexpected Observation**: Removing Heterogeneous edges dramatically reduced VRAM consumption (down 0.7 GB) and inference latency. For edge devices or low-compute environments, a Homogeneous variant of AgileGraph might actually be preferred despite the 5% F1-score penalty.

**Threat to Validity**: The ablation study currently only disables components independently. It does not measure higher-order interaction effects (e.g., removing *both* GATv2 and Heterogeneous edges simultaneously), which might trigger non-linear performance decay. Future factorial design studies are recommended.
