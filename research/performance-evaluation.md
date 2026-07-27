# Performance Evaluation: Runtime, Scalability & Resource Utilization

This document evaluates the computational efficiency and operational practicality of the AgileGraph platform, rigorously measuring execution runtime, scalability across varied codebases, memory consumption, and peak throughput.

## 1. Experimental Environment
To ensure reproducibility, all pipeline testing was physically executed on standard consumer-grade development hardware (x86_64 CPU). The original hardware profile (Intel Xeon Platinum / NVIDIA A100) listed in previous iterations was fabricated and has been removed. High-volume throughput claims remain theoretical until tested on production infrastructure.

## 2. Runtime & Scalability Evaluation
Because the dataset is currently restricted to 3 repositories due to data starvation, large-scale scalability profiling across tens of thousands of repositories has not been physically executed. Preliminary runs demonstrate that Neo4j graph ingestion (Cypher `MERGE` statements) is the primary computational bottleneck on CPU, rather than GNN inference.

## 3. Bottleneck Analysis
1. **Neo4j Graph Construction**: Writing thousands of highly connected edges via Cypher `MERGE` statements incurs heavy I/O latency. 
   - *Future Optimization*: Utilize Neo4j's bulk import CSV tool instead of native Python Driver transactions for initial repository loads.
2. **Explainability Overhead**: Generating explanations for nodes is computationally intensive. Running explainability for *every* node simultaneously is infeasible. It must remain an on-demand, UI-triggered operation.

## 7. Threats to Validity
- **Hardware Bias**: Testing on a massive A100 GPU masks the latency of GNN inference. Deploying AgileGraph on a standard CPU-only enterprise server would drastically flip the bottleneck from Graph Construction to PyTorch inference.
