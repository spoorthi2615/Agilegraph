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
- **Heterogeneous Graph Utility**: While the model successfully generalizes (F1 > 0.47), ablation testing demonstrates that defining separate edge types (CALLS, INHERITS, IMPORTS) via a Heterogeneous graph structure provides no additional predictive value over a standard Homogeneous graph, while adding significant computational overhead.
- **Hardware Profile**: The platform has been tested on standard developer hardware (CPU), not a supercomputing cluster (A100/Xeon). High-volume throughput claims remain theoretical until tested on production infrastructure.
- **Data Imbalance**: The dataset (though expanded to 40 repositories) remains highly imbalanced (87% Safe vs 12% Vulnerable). While the F1 score reflects true generalization, Recall is still relatively low compared to Precision.

## 3. Future Work
Future iterations should explore larger Graph Isomorphism Networks (GIN) and further scale the corpus to hundreds of repositories to bridge the remaining structural shifts between specific cryptographic library versions.
