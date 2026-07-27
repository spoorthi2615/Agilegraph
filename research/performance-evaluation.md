# Performance Evaluation: Runtime, Scalability & Resource Utilization

This document evaluates the computational efficiency and operational practicality of the AgileGraph platform, rigorously measuring execution runtime, scalability across varied codebases, memory consumption, and peak throughput.

## 1. Experimental Environment
To ensure total reproducibility, all tests were executed within the following fixed hardware and software footprint:
- **CPU**: Intel Xeon Platinum 8380 (2.00 GHz, 40 Cores)
- **GPU**: NVIDIA A100 (40GB VRAM) (Used exclusively for GNN Inference & Explainability)
- **RAM**: 128 GB DDR4 ECC
- **Storage**: 2TB NVMe SSD
- **OS**: Ubuntu 22.04 LTS
- **Python**: v3.11.7
- **PyTorch**: v2.1.0+cu118
- **Neo4j**: Enterprise v5.15.0
- **Docker**: v24.0.7
- **Node**: v20.11.0 (Frontend rendering validation)

## 2. Runtime Evaluation
Each discrete pipeline stage was executed 10 times over a standardized "Medium" repository (50,000 LOC, ~1,500 functions).

| Pipeline Stage | Mean (s) | Median (s) | Min (s) | Max (s) | Std Dev (s) |
|---|---|---|---|---|---|
| Archive Upload & Decompression | 0.85 | 0.82 | 0.78 | 1.10 | 0.09 |
| Static AST Scanning & Parsing | 12.4 | 12.2 | 11.5 | 14.8 | 1.15 |
| Graph Construction (Neo4j Ingestion) | 18.2 | 17.8 | 16.5 | 22.1 | 1.84 |
| Feature Vector Generation | 4.5 | 4.3 | 4.1 | 5.6 | 0.42 |
| **GNN Model Inference** | **0.16** | **0.16** | **0.15** | **0.18** | **0.01** |
| Explainability (GNNExplainer per node) | 2.1 | 2.0 | 1.8 | 2.6 | 0.25 |
| Report Generation (Markdown/CSV) | 1.2 | 1.1 | 1.0 | 1.6 | 0.18 |

**Analysis**: Model Inference on the A100 is nearly instantaneous. The vast majority of the pipeline execution time is spent natively parsing the AST (12.4s) and marshaling that relational data into Neo4j (18.2s).

## 3. Memory Evaluation
Memory measurements were captured using `docker stats` and `torch.cuda.memory_allocated()`.

| Subsystem / Pipeline Stage | Peak RAM | Peak VRAM (GPU) |
|---|---|---|
| Neo4j Container (Idle) | 1.2 GB | 0 GB |
| Neo4j Container (Graph Construction) | 4.8 GB | 0 GB |
| FastAPI Backend (AST Parsing) | 2.1 GB | 0 GB |
| FastAPI Backend (GNN Inference) | 2.5 GB | 3.2 GB |
| Explainability Generation | 2.8 GB | **5.4 GB** |

**Analysis**: Explainability requires significantly more GPU VRAM than standard inference due to the computational overhead of calculating edge masks and gradients across the neighborhood subgraphs.

## 4. Scalability Evaluation
Evaluated across 4 distinct repository scales.

| Scale | LOC Size | Nodes | Edges | Runtime (Total) | Peak RAM |
|---|---|---|---|---|---|
| Small | < 10,000 | 850 | 1,200 | 8.5 s | 1.5 GB |
| Medium | ~ 50,000 | 4,500 | 8,900 | 38.4 s | 4.8 GB |
| Large | ~ 250,000 | 22,000 | 45,000 | 185.2 s | 12.4 GB |
| Very Large | > 1,000,000 | 95,000 | 215,000 | 845.0 s | 31.8 GB |

**Analysis**: The pipeline scales linearly ($O(N)$) with respect to lines of code. However, Neo4j graph ingestion exhibits slight super-linear scaling delays as the number of edges crosses 200,000 due to transaction batching overhead.

## 5. Throughput Evaluation
- **Repositories Processed**: ~110 Medium Repositories / Hour
- **Inference Throughput**: ~28,000 Nodes / Second (Batched Matrix Multiplication)
- **Graph Construction**: ~490 Edges / Second

## 6. Bottleneck Analysis
1. **Slowest Stage**: Neo4j Graph Construction. Writing thousands of highly connected edges via Cypher `MERGE` statements incurs heavy I/O latency. 
   - *Future Optimization*: Utilize Neo4j's bulk import CSV tool instead of native Python Driver transactions for initial repository loads.
2. **Explainability Overhead**: Generating explanations for a single node takes 2.1 seconds. Running explainability for *every* node simultaneously is computationally infeasible. It must remain an on-demand, UI-triggered operation.

## 7. Threats to Validity
- **Hardware Bias**: Testing on a massive A100 GPU masks the latency of GNN inference. Deploying AgileGraph on a standard CPU-only enterprise server would drastically flip the bottleneck from Graph Construction to PyTorch inference.
