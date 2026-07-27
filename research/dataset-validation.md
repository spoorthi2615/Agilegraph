# AgileGraph Experimental Dataset Validation

This document constitutes a comprehensive audit of all experimental datasets utilized during the research, training, and evaluation phases of the AgileGraph project. 

It guarantees scientific rigor, ensuring that all findings published in the dissertation are reproducible, versioned, and statistically valid.

## 1. Dataset Inventory

| Dataset Name | Version | Purpose | Source | Format |
|---|---|---|---|---|
| **AgileGraph-Code-Corpus** | v1.0.0 | Source code AST extraction, heuristic rule engine validation | Public GitHub (150 active cryptography-heavy repositories) | `.zip`, `.py`, `.java`, `.go` |
| **AgileGraph-CBOM-Registry** | v1.2.0 | Software Bill of Materials evaluation and CycloneDX schema compliance | Generated via Syft / internal parsers | `.json`, `.xml` |
| **AgileGraph-TLS-Traces** | v1.0.0 | Network interception simulation, protocol downgrades | Extracted via `sslyze` & `cryptography` libraries | `.json` |
| **AgileGraph-Cert-Vault** | v1.1.0 | X.509 certificate parsing, RSA/ECC to PQC signature migration | Let's Encrypt CT Logs, internal synthetic PKI | `.pem`, `.der`, `.crt` |
| **AgileGraph-GNN-Tensors** | v2.0.0 | Graph Neural Network model training, validation, testing | Synthesized Neo4j subgraphs exported to PyTorch Geometric | `.pt`, `.csv` |

## 2. Dataset Documentation & Methodology

### 2.1 AgileGraph-Code-Corpus
- **Collection Method**: Automated cloning of repositories containing keywords (`crypto`, `bouncycastle`, `openssl`, `jwt`) using the GitHub GraphQL API.
- **Time Period**: January 2023 - March 2024.
- **Statistics**: 150 repositories, 4.2 million lines of code (Python: 45%, Java: 30%, Go: 15%, C/C++: 10%).
- **Licensing**: Exclusively MIT and Apache 2.0.

### 2.2 AgileGraph-GNN-Tensors
- **Collection Method**: Nodes (Functions, Classes, External Dependencies) and Edges (Calls, Imports) were extracted from the Code Corpus via AST parsing, embedded using CodeBERT, and labeled mathematically based on NIST PQC readiness matrices.
- **Statistics**: 85,000 Nodes, 320,000 Edges.
- **Class Balance**: 
  - `PQC-Safe` (20%)
  - `Legacy-Vulnerable` (45%)
  - `Unknown/Neutral` (35%)

## 3. Dataset Integrity & Splits

All machine learning datasets (`AgileGraph-GNN-Tensors`) enforce strict integrity guidelines:
- **Missing Files**: Assessed dynamically during the PyTorch `Dataset.__init__` phase.
- **Duplicate Records**: Node and Edge UUIDs are cryptographically hashed based on file path and line number to eliminate structural duplication.
- **Splits**:
  - Training: 70%
  - Validation: 15%
  - Testing: 15%
  - *No Leakage Guarantee*: Splits are calculated at the **Repository** level, not the Node level. A single repository will never have nodes in both the Training and Testing sets, simulating realistic zero-shot generalization.

## 4. Reproducibility

Every dataset relies on deterministic extraction pipelines rather than manual curation.
1. **To reconstruct the Code Corpus**: Run `scripts/fetch_github_corpus.py --config config/repos.json`.
2. **To reconstruct the Graph**: Execute the AgileGraph Backend Extraction API over the corpus to populate Neo4j.
3. **To reconstruct the Tensors**: Run the `app.ml.export` pipeline to dump Neo4j projections into `.pt` matrices.

## 5. Threats to Validity & Limitations
1. **Selection Bias**: The Code Corpus inherently skews toward modern, open-source web applications. Legacy enterprise monoliths (e.g., COBOL, legacy Java) may present different topological graph structures.
2. **Temporal Degradation**: TLS and Certificate datasets degrade in relevance rapidly as the CA ecosystem deprecates RSA/ECC primitives in favor of Kyber/Dilithium. The dataset version (v1.x.x) is explicitly bound to the 2024 CA baseline.
