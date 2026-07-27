# Research Validity Testing Protocol

This document outlines the testing protocols established in Sprint 79.6 to audit the transparency, reproducibility, and generalizability claims of the AgileGraph dissertation.

## 1. Reproducibility Configuration Audit
1. Navigate to the root directory of the AgileGraph repository.
2. Execute the verification script: `python -m scripts.verify_reproducibility_artifacts`.
3. **Verify**: The script must confirm the presence and checksum validity of:
   - `Dockerfile` (Backend & Frontend)
   - `docker-compose.yml`
   - `requirements.txt` (Python bindings)
   - `package-lock.json` (NPM bindings)
4. **Why**: Ensures that an independent researcher has access to the exact orchestrational state used during the empirical studies, eliminating environmental drift.

## 2. Dataset Version Tracking Test
1. Inspect the published model weights (`models/agilegraph_gnn_v1.pt`).
2. Read the embedded PyTorch metadata dictionary attached to the state dictionary.
3. **Verify**: The metadata must explicitly reference `AgileGraph-GNN-Tensors v2.0.0` and `Seed: 42`.
4. **Why**: Prevents version mismatch errors where future researchers attempt to evaluate a legacy model against a newly extracted dataset.

## 3. Generalizability Limitation Validation
1. Review the AST parser mapping configurations (`app.analysis.parsers`).
2. **Verify**: C++ and Rust parsers are formally marked as `NotImplemented` or `Experimental`.
3. **Why**: Acts as a code-level enforcement of the External Validity claims published in `threats-to-validity.md`, preventing undocumented overreach in the dissertation's scope.

## 4. Documentation Cohesion Check
1. Search the full repository markdown files for mentions of "100% accuracy" or "guaranteed detection".
2. **Verify**: No absolute guarantees exist.
3. **Why**: Enforces scientific integrity. The limitations regarding "Dead Code False Positives" and "Dynamic Runtime Injection Blindspots" must remain explicitly visible across all deployment and research documentation.
