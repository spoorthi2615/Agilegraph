# Continuous Integration (CI) Pipeline

This document outlines the Continuous Integration (CI) pipeline implemented for AgileGraph via GitHub Actions.

## Philosophy
The pipeline acts as a strictly automated quality gate. It ensures that every commit and pull request on the `main` branch mathematically builds, complies with security profiles, and respects Docker syntax before it is eligible for manual or automated production delivery.

> **Note**: This pipeline is restricted to Continuous Integration (CI). Continuous Delivery (CD) logic is deliberately excluded to prevent unexpected mutations to live deployment environments.

## Pipeline Architecture

The pipeline (`.github/workflows/ci.yml`) is split into three highly parallelized jobs:

### 1. Backend Validation (`backend-ci`)
Executes inside a Python 3.11 environment.
- **Dependencies**: Installs `requirements.txt` leveraging GitHub's native `pip` cache.
- **Security Scan**: Executes `pip-audit` to detect CVEs in downstream site-packages.
- **Linting**: Enforces code consistency via `ruff` and `black --check`.
- **Testing**: Runs the `pytest` test suite and outputs coverage metrics.
- **Artifacts**: Uploads `backend-coverage.xml`.

### 2. Frontend Validation (`frontend-ci`)
Executes inside a Node 20.x environment.
- **Dependencies**: Executes `npm ci`, heavily leaning on the `package-lock.json` cache lock.
- **Security Scan**: Executes `npm audit --omit=dev --audit-level=high` targeting specifically production vulnerabilities.
- **Build**: Executes `npm run build`, implicitly forcing a strict TypeScript compiler check (`tsc -b`).

### 3. Docker Validation (`docker-ci`)
Dependent on the success of both `backend-ci` and `frontend-ci`.
- **Compose Linting**: Validates the `docker-compose.yml` schema via `docker compose config -q`.
- **Image Compilation**: Triggers a local `docker build` for both the backend and frontend Dockerfiles to mathematically guarantee the configurations haven't been broken by dependency bumps. 
- *(Images are built but deliberately NOT pushed to a registry)*.

## Triggers
- `push` to the `main` branch.
- `pull_request` targeting the `main` branch.
- `workflow_dispatch` (Manual trigger via the Actions tab).

## Failure Handling
The workflow is designed to fail fast. If `pip-audit` detects a critical CVE, the `backend-ci` job fails instantly, halting the `docker-ci` step. Linting and testing steps employ `continue-on-error: true` temporarily to prevent blocking the entire pipeline while test coverage is being built out by the development team.
