# Threats to Validity & Reproducibility Audit

*This file is hand-maintained; when the corpus or ablation results change materially, update it manually — it is not covered by `scripts/generate_*.py`.*
This document serves as a critical audit of the AgileGraph research methodology, empirically assessing internal vulnerabilities, generalization boundaries, statistical limitations, and systemic reproducibility constraints.

## 1. Internal Validity
Internal validity assesses whether the experimental outcomes are mathematically sound or a byproduct of confounding variables.
- **Data Leakage**: Mitigated. Train, Validation, and Test splits were rigidly enforced at the repository level. No nodes from a training repository exist in the testing matrix.
- **Selection Bias**: Present. The dataset consists of 40 open-source repositories across 3 languages (Java, Python, Go) from GitHub heavily utilizing public libraries (`cryptography`, `bouncycastle`, etc.). It systematically excludes proprietary, isolated enterprise codebases.
- **Random Seed Dependence**: Mitigated. All experimental benchmarks (Sprint 79.2) and ablations (Sprint 79.5) explicitly froze Python, NumPy, and PyTorch seeds (`42`), mathematically neutralizing initial weight lottery variance.
- **Measurement Bias**: Mitigated. The ground-truth node labels were generated using strict NIST PQC migration guidelines rather than subjective human annotation.

## 2. External Validity (Generalizability)
External validity defines the boundaries of the research's applicability to the broader software ecosystem.
- **Language Boundaries**: AgileGraph's AST parsers currently focus on Python, Java, and Go. The GNN's topological reasoning *hypothetically* applies to C++ or Rust, but this has not been empirically proven within this study.
- **Closed-Source Enterprise Generalization**: Limited. AgileGraph heavily relies on CodeBERT contextual embeddings. Enterprise environments utilizing heavily obfuscated variable names or non-standard naming conventions (e.g., `do_enc()` instead of `aes_encrypt()`) will likely see a degradation in F1-score as the NLP embeddings fail to capture intent.

## 3. Construct Validity
- **Evaluation Metrics**: The selection of F1-Score and ROC-AUC is mathematically appropriate given the inherent class imbalance of cryptographic nodes (PQC-Safe vs Legacy vs Neutral). Relying solely on raw Accuracy would have superficially inflated model performance.
- **Explainability**: The implementation of GNNExplainer provides high theoretical construct validity by mapping neural predictions directly back to specific edges and syntax lines, directly supporting human decision-making during security audits.

## 4. Conclusion Validity
- **Statistical Significance**: High. McNemar's Test establishes statistical significance ($p < 10^{-22}$), and 1,000-iteration empirical bootstrap confidence intervals confirm model stability.
- **Effect Sizes**: Appropriate. Cohen's Kappa statistics validate that the Full Model's accuracy far exceeds random chance despite class imbalances.

## 5. Research Assumptions & Limitations
1. **Static Analysis Completeness**: AgileGraph assumes that static AST compilation adequately represents runtime execution. It inherently fails to track dynamic cryptographic material loaded via runtime dependency injection or JNI/C-bindings.
2. **Graph Abstraction Accuracy**: We assume the Neo4j extraction schema (Nodes=Functions/Classes, Edges=CALLS/IMPORTS) captures sufficient cryptographic context without overwhelming the GNN message-passing mechanism with trivial syntax nodes.
3. **Dead Code Sensitivity**: The static extraction does not filter unexecuted code paths, leading to documented False Positives where legacy algorithms are imported but never invoked.

## 6. Reproducibility & Replicability Audit
An independent researcher can fundamentally reconstruct this study using the following fixed artifacts:
- **Environment**: Docker v24.0, Python 3.11.7, PyTorch 2.1.0+cu118.
- **Datasets**: `AgileGraph-Code-Corpus v1.0.0` and `AgileGraph-GNN-Tensors v2.0.0`.
- **Scripts**: `/scripts/run_benchmarks.py` and `/scripts/generate_ablation_figures.py`.
- **Replicability**: High on standard hardware. Replicating the exact latency metrics (~30-40ms inference) requires similar modern multi-core CPU architecture. Running on significantly older consumer hardware or massive distributed clusters will yield different timing topologies.

## 7. Future Threats to Validity
- **Evolution of PQC Standards**: NIST's finalization of FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) may shift software development paradigms. If standard libraries natively abstract PQC negotiation away from the application layer, the relevance of AgileGraph's manual topological detection may diminish over time.
- **CodeBERT Degradation**: As programming syntax evolves, the frozen Microsoft CodeBERT weights utilized in this study will suffer from linguistic drift, necessitating future fine-tuning regimes.
