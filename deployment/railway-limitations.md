# Railway Deployment — Known Limitations

## ML Dependencies Intentionally Excluded

The production Docker image (`backend/Dockerfile`) installs only `requirements-prod.txt`.
The ML stack — `torch`, `torch_geometric`, and `transformers` (CodeBERT) — is **deliberately omitted** because Railway's free/hobby tier imposes a ~512 MB RAM ceiling that torch alone exceeds at runtime.

### What works on Railway (API-only mode)
| Feature | Status |
|---|---|
| Dashboard, Graph View, Risk Rankings | ✅ Fully operational (Neo4j-backed) |
| Mosca Readiness scoring | ✅ Fully operational |
| Reports generation | ✅ Fully operational |
| Explainability queries | ✅ Operational for pre-computed results |
| File upload / GitHub import (trigger) | ✅ Upload accepted, project ID returned |
| **GNN inference during scan** | ⚠️ Gracefully skipped — falls back to heuristic scores |
| **CodeBERT embedding generation** | ⚠️ Gracefully skipped — heuristic risk scores used instead |

### What happens when a scan is triggered on Railway

The scan background task (`analysis_workflow_service.py`, step 3.5) already contains a `try/except` that catches `ImportError` and `RuntimeError` from missing torch/transformers:

```python
except Exception as ml_err:
    logging.warning(f"[{project_id}] ML Inference skipped (using heuristic scores): {ml_err}")
```

This means scans **do complete** on Railway — they just use the heuristic risk scorer instead of GATv2+CodeBERT predictions. The scan status will be `completed` and results will be visible in the dashboard. The quality of risk scores is lower than the full ML pipeline, but the system does not crash or hang.


### Running locally with full ML pipeline

```bash
pip install -r backend/requirements.txt   # includes torch, torch_geometric, transformers
uvicorn app.main:app --reload --port 8000
```

Full GNN scan → Neo4j ingestion → explainability pipeline works end-to-end locally.

### Upgrading to production ML deployment

To enable GNN on a deployed instance:
1. Switch to a higher-memory tier (Railway Pro, AWS EC2 `t3.large`, or GCP `e2-standard-2`)
2. Change `Dockerfile` line 11 from `requirements-prod.txt` → `requirements.txt`
3. Optionally use `requirements-prod.txt` as a base and add only `torch==2.1.0+cpu` for CPU-only inference

> **Research note:** For the purposes of this project evaluation, the GNN pipeline is validated locally and via `scripts/run_experiments.py`. The Railway deployment serves as a live API/dashboard demo only.
