# Ablation Study Validation Protocol

This document outlines the testing protocols established in Sprint 79.5 to empirically verify the isolation, execution, and interpretation of the AgileGraph ablation study.

## 1. Component Isolation Verification
1. Open the PyTorch Geometric model configuration script (`app.ml.models.agilegraph_gnn`).
2. **Verify**: Ensure that feature toggles exist (e.g., `use_heterogeneous_edges=True`, `use_gatv2=True`, `use_edge_attrs=True`) and that disabling them physically routes the tensor math through alternative homogeneous or GraphSAGE blocks.
3. **Why**: To guarantee that setting a flag physically bypasses the isolated component rather than just masking its output late in the network, which would invalidate the latency measurements.

## 2. Experimental Consistency Verification
1. Inspect the 5 discrete training logs generated during the ablation study.
2. **Verify**: The PyTorch DataLoader random seeds, learning rates (AdamW), and cross-entropy loss functions must match exactly across all 5 logs.
3. **Verify**: The epoch count at early-stopping must correlate exclusively to validation loss degradation rather than manual intervention.

## 3. Metric Calculation & Visual Validation
1. Execute the manual generation script: `python scripts/generate_ablation_figures.py`.
2. Inspect `research/figures/ablation_f1_drops.png`.
3. **Verify**: The visual degradation cascade matches the numerical subtractions calculated in the publication tables (`-0.129` for CodeBERT, `-0.053` for Heterogeneous Edges, etc.).
4. **Why**: Guarantees the dissertation graphics mathematically mirror the underlying evaluation matrices without subjective visual skewing (e.g., misleading y-axis truncations).

## 4. Hardware Latency Validation
1. Cross-reference the recorded runtime latency for the Homogeneous variant (110.5 ms) against the Full Heterogeneous variant (165.2 ms).
2. **Verify**: The 33% reduction in latency mathematically aligns with the theoretical reduction in PyTorch message passing operations when isolated weight matrices are collapsed into a single uniform transformation.
