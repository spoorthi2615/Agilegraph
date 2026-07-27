# Current Status & Known Limitations

This document serves as an honest appraisal of the current state of the AgileGraph research project. 
It replaces prior versions of the final certification document which incorrectly claimed statistical significance and hardware evaluations that were not physically run.

## 1. System Status
The AgileGraph implementation is physically sound and functionally complete. 
- **Graph Neural Network**: The PyTorch Geometric pipeline (including `GATv2NodeClassifier`) is fully implemented and correctly executes inference.
- **Scanners**: Structural static analysis, OSV.dev dependency checking, Semgrep integration, and Certificate Transparency log polling are fully wired and functional.
- **UI Integration**: The frontend correctly fetches real data from the FastAPI backend and visualizes the Neo4j graph.
- **Integration Testing**: A genuine integration test (`e2e_integration_test.py`) has replaced prior fabricated testing claims, confirming that the pipeline physically executes.

## 2. Known Limitations
- **Data Starvation & F1 Collapse**: The most significant limitation is the training corpus size. Evaluated on just 3 repositories (WebGoat, Paramiko, Vault), the GNN suffers from an empty test-split (or a completely overfitted 1-repo test split), resulting in a mathematical inability to generalize (F1-score = 0.000). The corpus must be scaled to 10+ repositories to measure true generalization.
- **Hardware Profile**: The platform has been tested on standard developer hardware (CPU), not a supercomputing cluster (A100/Xeon). High-volume throughput claims remain theoretical until tested on production infrastructure.
- **Statistical Power**: Because the corpus is n=3, McNemar's testing and Cohen's Kappa statistics cannot be established. No statistical significance is claimed.

## 3. Future Work
The immediate next step is running `fetch_github_corpus.py` on the expanded 10-repository list in `config/repos.json`. Expanding the dataset is the sole critical path to unlocking the GNN's ability to learn cross-repository representations.
