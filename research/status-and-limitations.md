# Current Status & Known Limitations

This document serves as an honest appraisal of the current state of the AgileGraph research project. 
It replaces prior versions of the final certification document which incorrectly claimed statistical significance and hardware evaluations that were not physically run.

## 1. System Status
The AgileGraph implementation is physically sound and functionally complete. 
- **Graph Neural Network**: The PyTorch Geometric pipeline (including `GATv2Model`) is fully implemented and correctly executes inference.
- **Scanners**: Structural static analysis, OSV.dev dependency checking, Semgrep integration, and Certificate Transparency log polling are fully wired and functional.
- **UI Integration**: The frontend correctly fetches real data from the FastAPI backend and visualizes the Neo4j graph.
- **Integration Testing**: A genuine integration test (`e2e_integration_test.py`) has replaced prior fabricated testing claims, confirming that the pipeline physically executes.

## 2. Known Limitations
- **Zero-Shot Generalization Failure**: Even after expanding the training corpus to 10 repositories, the GNN completely fails to generalize to unseen test repositories (F1-score = 0.000). While early validation metrics appeared to show the model learning (F1 ~ 0.38), ablation testing revealed this peak score occurred when CodeBERT semantic embeddings were replaced with random noise. This implies the model is likely overfitting to graph structural shortcuts (like node degrees) rather than genuinely learning code semantics, resulting in a massive structural domain shift when applied to new codebases.
- **Hardware Profile**: The platform has been tested on standard developer hardware (CPU), not a supercomputing cluster (A100/Xeon). High-volume throughput claims remain theoretical until tested on production infrastructure.
- **Statistical Power**: Because the test classification predictions are identically 0, McNemar's testing and Cohen's Kappa statistics cannot be established. No statistical significance is claimed.

## 3. Future Work
Future iterations must explore more advanced Domain Adaptation techniques or dramatically scale the corpus to hundreds of repositories to bridge the structural shift between projects.
