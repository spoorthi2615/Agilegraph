# Performance Evaluation Validation Protocol

This document outlines the testing protocols established in Sprint 79.4 to empirically verify the runtime, memory, and scalability measurements of AgileGraph.

## 1. Timing Consistency Test
1. Execute the AgileGraph pipeline over a standard Medium repository (e.g., a stripped-down `openssl` mirror).
2. Read the structured JSON logs emitted by the backend middleware.
3. **Verify**: The duration field (`process_time`) across 10 distinct uploads must yield a standard deviation of less than 2.0 seconds. 
4. **Why**: Ensures that the runtime evaluation numbers published in the dissertation are representative of average performance rather than cherry-picked cold-start or warm-cache anomalies.

## 2. Memory Bottleneck Verification
1. Open three terminal panes.
2. In Pane 1: Run `watch docker stats` to monitor container-level RAM.
3. In Pane 2: Run `watch nvidia-smi` to monitor GPU VRAM.
4. In Pane 3: Trigger an Explainability request for a highly connected node.
5. **Verify**: Observe VRAM spike to ~5.4 GB, confirming the memory calculations published in the evaluation tables. Observe Neo4j memory consumption spike during graph ingestion but stabilize post-commit.

## 3. Publication Figure Generation
1. Run `python scripts/generate_performance_figures.py`.
2. Navigate to the `research/figures/` directory.
3. **Verify**: The script successfully outputs `runtime_vs_size.png`, `memory_vs_size.png`, and `throughput_analysis.png`.
4. **Verify**: The visual curves logically map to the data constraints measured in the publication tables (e.g., verifying the linear scaling of runtime vs size).
