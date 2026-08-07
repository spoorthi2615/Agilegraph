---
title: Agilegraph API
emoji: 🚀
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 4.36.1
app_file: main.py
pinned: false
---

# AGILEGRAPH: Graph-Learned Crypto-Agility Risk Scoring for Post-Quantum Migration

**AgileGraph** is a full-stack, production-ready platform designed to analyze source code repositories, construct cryptographic knowledge graphs, and evaluate cryptographic agility using advanced heuristic algorithms and Graph Neural Networks (GNNs). 

This project provides end-to-end organizational visibility into cryptographic assets and their readiness for the upcoming Post-Quantum Cryptography (PQC) transition.

## 🚀 Key Features

### 🔍 Multi-Vector Cryptographic Discovery
AgileGraph employs a multi-faceted scanning approach to discover cryptographic usage across an enterprise:
- **Language Parsers**: Native structural analysis for Java, Python, and Go repositories.
- **Dependency Scanning**: Transitive risk analysis for third-party libraries.
- **Certificate Scanners**: Extracts embedded repository certificates and performs **Live TLS** analysis on deployed assets.
- **Certificate Transparency (CT)**: Passive OSINT querying of historical public certificate logs.
- **Static Analysis (Semgrep)**: Secure subprocess integration for deep security pattern matching.
- **CBOM Integration**: Bidirectional comparison using Cryptographic Bills of Materials to validate discovered assets against external baselines.

### 🕸️ Knowledge Graph Construction
All discovered assets are normalized and mapped into a dense structural representation using **Neo4j**.
- Connects Repositories → Files → Functions → Cryptographic Primitives.
- Embeds metadata like algorithm strength, key sizes, and execution contexts.
- Resolves risk propagation automatically across transitive dependencies.

### 🧠 Graph Neural Network (GNN) Intelligence
AgileGraph leverages PyTorch Geometric to train and deploy a **GATv2 (Graph Attention Network v2)**.
<!-- AUTO-GENERATED:RESULTS:START -->
- **Mathematically Verified:** Over 40 diverse repositories, AgileGraph achieves a statistically significant Macro-F1 of **0.913** via its Full Model (w/ Heuristic) formulation, definitively defeating random noise baselines ($p < 10^{-22}$ via McNemar's Test).
- **Industry Baselines:** We evaluated AgileGraph against industry tools like IBM's CBOMkit. However, because `cbomkit-theia` evaluates filesystems rather than deep source-code heuristics, its output is currently scoped as N/A for this pure-source corpus to avoid deceptive baseline numbers (See `research/benchmark-study.md` for our transparent findings).
<!-- AUTO-GENERATED:RESULTS:END -->
- Includes **GNNExplainer** integration (Explainable AI) to expose exactly which node features and edges led the neural network to its decision.

### ⚖️ Heuristic Scoring & Sensitivity Analysis
A deterministic, mathematically verifiable rules engine operates alongside the ML models:
- Computes baseline risk penalties for Algorithm Strength, Certificate Weakness, Dependency Risk, Exposure, and Graph Centrality.
- Features a **Sensitivity Analysis Framework** to mathematically prove the robustness of the heuristic weightings.

### 🛡️ Migration Intelligence
Actionable insights for security engineers:
- **Migration Estimator**: Mathematically calculates the percentage reduction in overall organizational risk if a vulnerable asset is migrated to a PQC-ready alternative.
- **Recommendation Engine**: Automatically prioritizes migration paths based on risk severity, GNN confidence, and overall migration effort.

### 📊 Interactive React Dashboard
The platform features a rich, responsive frontend (`frontend-1/`) built to visualize the complex outputs of the backend:
- **Interactive Graph Canvas**: Navigate the Neo4j knowledge graph visually.
- **Risk Dashboards**: Real-time breakdown of Post-Quantum migration readiness, critical vulnerabilities, and algorithm distributions.
- **ML & Explainability Panels**: Review GNN predictions and the underlying feature importance.
- **Experiment Reports**: Downloadable insights across Statistical Bootstrapping, Cohen's Kappa baselines, and Sensitivity Analyses.

---

## 🏗️ Full-Stack Architecture

AgileGraph strictly adheres to **Clean Architecture**, **SOLID Principles**, and **Dependency Injection** across its stack.

### Backend (`backend/`)
Built with Python, powering the core ingestion, scanning, and analytical pipelines.
- `app/scanners/`: Domain-specific discovery engines (Semgrep, TLS, CBOM, etc).
- `app/graph/`: Neo4j abstraction layer and edge-mapping logic.
- `app/explainability/`: PyTorch Geometric ML models and Explainable AI integrations.
- `app/heuristics/`: Rule-based risk estimators and Migration Prioritization.
- `app/dashboard/`: Facade aggregators exposing structural data to the React UI.

### Frontend (`frontend-1/`)
A modern, component-driven React application designed for high-density data visualization.
- `src/components/widgets/`: Reusable visualization components (e.g., `crypto-graph-canvas.tsx`).
- Consumes the aggregated `DashboardPayload` provided by the backend Facade layer.

---

## 🧪 Testing & Validation

The platform includes a genuine integration testing framework:
- **End-to-End Integration**: Executes the full `ProjectAnalysisService` against real repositories (like WebGoat) to validate that structural static analysis, Semgrep scanning, and OSV.dev dependency checking correctly generate actionable findings and graph nodes.

Run the Backend End-to-End validation suite:
```bash
python backend/tests/e2e_integration_test.py
```
---

## 🛡️ Security & Performance

- **SSRF Hardened**: All external network calls (Live TLS, CT Logs) are strictly validated against authorized domains. Subprocesses (Semgrep) are executed in secure, immutable isolation.
- **Fault Tolerant**: Uses abstract Provider Interfaces and `try/except` fallbacks so the Frontend will *never* crash if an underlying database or ML model goes offline.
- **Optimized UI**: The React frontend leverages optimized graph rendering techniques to handle complex cryptographic topologies efficiently.

---

## 🛠️ Getting Started & Deployment

AgileGraph is designed to be deployed locally for development or via Docker for production environments.

### Prerequisites
- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **Neo4j** (Graph Database)
- **Git**

### 1. Database Setup (Neo4j)
AgileGraph requires a running instance of Neo4j. You can start one quickly using Docker:
```bash
docker run -d --name neo4j-agilegraph \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 2. Backend Setup
Navigate to the `backend/` directory, set up your environment variables, and install the Python dependencies.
```bash
cd backend
cp .env.example .env
# Edit .env and fill in your own credentials/keys
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

Run the backend FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
Navigate to the `frontend-1/` directory, set up your environment variables, and install the Node modules.
```bash
cd frontend-1
cp .env.example .env
# Edit .env and fill in your own credentials if needed
npm install
```

Start the React development server:
```bash
npm run dev
```

The AgileGraph Dashboard will now be accessible at `http://localhost:3000`, communicating with the backend API at `http://localhost:8000`.

---

## 🎓 Academic Context
This repository represents the comprehensive implementation for a dissertation evaluating Cryptographic Agility and Post-Quantum readiness using Structural Graph Analysis and Machine Learning. The implementation has successfully evaluated over 21,000 cryptographic nodes across 40 open-source repositories, demonstrating that Graph Neural Networks can successfully extract semantic topologies for vulnerability prediction, while also highlighting the computational efficiency of homogeneous vs heterogeneous structures.
