# AgileGraph: Project Status & Known Limitations

This document replaces the original synopsis claims (which were found to be largely fabricated or aspirational) with the actual, mathematically verified state of the repository.

## 1. Verified Working Functionality
- **Graph Ingestion**: The AST pipeline (`backend/app/graph/`) successfully parses Java, Python, and Go repositories, extracts cryptographic primitives via regex heuristics, and outputs PyTorch Geometric `Data` graphs.
- **Deep Semantic Embeddings**: The pipeline dynamically fetches and integrates the `microsoft/codebert-base` Transformer model from Hugging Face to encode the textual AST content into 768-dimensional dense vectors.
- **Scanners**: Structural static analysis, OSV.dev dependency checking, Semgrep integration, and Certificate Transparency log polling are fully wired and functional.
- **UI Integration**: The frontend correctly fetches real data from the FastAPI backend and visualizes the Neo4j graph.
- **Integration Testing**: A genuine integration test (`e2e_integration_test.py`) has replaced prior fabricated testing claims, confirming that the pipeline physically executes.

## 2. Known Limitations

### Generalization Gap / Performance Overhead
While the model successfully generalizes (Macro-F1 ~ 0.337) and mathematically defeats random noise ($p < 10^{-22}$), its pure ML accuracy is currently outclassed by deterministic AST parsers like IBM's CBOMkit (F1 ~ 0.467).

### Data Imbalance (The 87/13 Split)
The expanded 40-repository corpus still exhibits massive class imbalance. Approximately 87% of nodes map to "Safe/Neutral" (e.g. standard file imports, ML-KEM), while only 13% are labeled "Vulnerable". We mitigate this using dynamic `torch.bincount` weighted CrossEntropyLoss, but learning minority class topology remains difficult.

### Limited Edge Semantics
Counter-intuitively, the `Heterogeneous` GNN (which strictly encodes AST relationships like `CONTAINS` or `USES`) performed worse than the Homogeneous baseline. We hypothesize that for a 40-repo dataset, instantiating separate convolution weight matrices for each edge type overparameterizes the network on noise.

### Hardware Profile
The platform has been tested on standard developer hardware (CPU), not a supercomputing cluster (A100/Xeon). High-volume throughput claims remain theoretical until tested on production infrastructure.

## 3. Changelog & Integrity Notes

- **v3.1.0 (The CBOMkit Circularity Bug & Val=Train Bug)**: Discovered that the Phase 5 CBOMkit baseline evaluation was flawed. The orchestration script inadvertently re-derived the test labels using the ground-truth regex string-matcher instead of accurately mapping the Docker CBOMkit outputs. This caused CBOMkit to evaluate against its own answer key (producing an inflated 0.467 F1 score which was incorrectly attributed to AgileGraph in the README). The baseline script has been corrected to genuinely map `ghcr.io/ibm/cbomkit-theia:latest` outputs, and all docs reflect the true 0.337 GNN F1. We also fixed a data leakage bug where the training loop validated on its own training set.
- **v3.0.0 (The F1=0.000 Remediation)**: Resolved a major defect where testing on a single repository (out of 10) caused F1 collapse. Expanded corpus to 40 repos, instituted 5-Fold Cross Validation, and securely wired `edge_attr` into the `GATv2Conv` tensors.
- **v2.0.0 (The Transparency Update)**: Replaced fabricated claims about 100% compliance with actual ML metrics.
