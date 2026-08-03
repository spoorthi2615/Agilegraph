# scripts/ Directory — File Naming Guide

## Python Scripts (executable)

| File | Purpose |
|---|---|
| `run_experiments.py` | Main GNN training + ablation runner — produces `research/results.json` |
| `generate_ablation_report.py` | Auto-generates `research/ablation-study.md` from results |
| `generate_benchmark_report.py` | Auto-generates `research/benchmark-study.md` |
| `generate_statistical_report.py` | Auto-generates `research/statistical-analysis.md` |
| `generate_ablation_figures.py` | Generates matplotlib figures → `research/figures/` |
| `generate_performance_figures.py` | Generates performance/latency figures |
| `generate_readme_snippet.py` | Generates the metrics badge block in `README.md` |
| `statistical_tests.py` | McNemar's test, bootstrapping, Cohen's Kappa |
| `generate_gnn_dataset.py` | Converts corpus → PyTorch Geometric tensors |
| `fetch_github_corpus.py` | Downloads the 40-repo training corpus |
| `run_cbomkit.py` | Runs IBM CBOMkit Docker baseline |
| `inspect_cbomkit_output.py` | Parses and summarises CBOMkit JSON output |
| `inspect_dataset.py` | Dataset statistics and class distribution |
| `lint_generated_docs.py` | CI cross-document consistency check |
| `check_doc_drift.py` | Detects stale auto-generated research docs |
| `report_helpers.py` | Shared utilities for all generator scripts |
| `verify_determinism.py` | Confirms seed-frozen reproducibility |
| `pin_repos.py` | Pins corpus repo SHAs for reproducibility |
| `statistical_tests.py` | Statistical significance tests |

## `test_*.md` Files — Manual QA Checklists (NOT pytest)

> ⚠️ Despite the `test_` prefix, **these are not automated tests**. They are manual QA checklists used to verify system behaviour during integration and release. They follow a checkbox format and are reviewed by the developer, not executed by CI.

The real automated test suite lives in **`backend/tests/`**:
- `backend/tests/test_ahp_lite.py` — unit tests for AHP-Lite expert weight module
- `backend/tests/e2e_integration_test.py` — end-to-end API integration tests
- `scripts/test_report_helpers.py` — unit tests for report helper utilities

The `test_*.md` naming was adopted for human discoverability during sprint reviews. A future refactor could rename them to `qa_*.md` to reduce ambiguity.

| Checklist | What it verifies |
|---|---|
| `test_ablation_validation.md` | Ablation run output sanity checks |
| `test_benchmark_validation.md` | Benchmark results plausibility |
| `test_dataset_validation.md` | Corpus size, class balance, label distribution |
| `test_cicd.md` | CI/CD pipeline health |
| `test_configuration.md` | Environment variable and settings validation |
| `test_docker_compose.md` | Docker Compose multi-service startup |
| `test_dockerization.md` | Individual container build and run |
| `test_observability.md` | Logging, metrics endpoint health |
| `test_performance_evaluation.md` | Runtime, latency, throughput checks |
| `test_release_certification.md` | Pre-release gate checklist |
| `test_final_research_certification.md` | End-to-end research reproducibility gate |
| `test_security_hardening.md` | CORS, rate limit, CSP headers verification |
| `test_statistical_analysis.md` | Statistical test output review |
| `test_research_validity.md` | Cross-document metric consistency |
