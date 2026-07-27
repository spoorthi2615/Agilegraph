# AgileGraph Release Certification Protocol (v1.0)

This document serves as the ultimate end-to-end certification checklist for AgileGraph's production deployment, ensuring the platform is ready for demonstration, research evaluation, and orchestration.

## 1. Full Deployment Validation
1. Clone the repository to a clean server environment.
2. Ensure no `.env` file exists (to test failure) and run `docker compose up --build -d`.
   - **Expectation**: Backend fails immediately via Pydantic `ValidationError`.
3. Provide `.env` with required secrets (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD).
4. Re-run `docker compose up -d`.
5. **Validation**:
   - `docker ps` shows Neo4j, Backend, and Frontend running.
   - Wait 15 seconds. Run `docker compose ps`. Backend health check transitions from `starting` to `healthy`.

## 2. Backend Validation
1. **Health/Metrics**:
   - `curl -s http://localhost:8000/api/v1/health/live` -> HTTP 200 `{"status": "alive"}`
   - `curl -s http://localhost:8000/api/v1/metrics` -> HTTP 200 (contains uptime, version)
2. **Security Headers**:
   - `curl -I http://localhost:8000/api/v1/health/live`
   - **Expectation**: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
3. **Logging**:
   - `docker logs agilegraph-backend`
   - **Expectation**: Standard JSON logs with `X-Request-ID` and environment context.
4. **Rate Limiting**:
   - Spam 70 requests to `/api/v1/analysis/assets`.
   - **Expectation**: Requests 61-70 return `429 Too Many Requests`.

## 3. Frontend Validation
1. Navigate to `http://localhost`.
2. **Expectation**: Dashboard loads successfully. Nginx serves React routing via `try_files`.
3. **Security**: Inspect network tab. The Nginx server responds with strict Content Security Policy (`default-src 'self'`).
4. **UI Workflows**: Navigate between Dashboard, Scan, Assets, Graph, Explainability, and Reports.

## 4. End-to-End Workflow Validation
1. **Upload**: Drop a ZIP archive via the frontend.
2. **Wait**: Observe loading state.
3. **Graph**: Open `/graph` and verify Neo4j nodes dynamically populate.
4. **Analysis**: Open `/rankings` and confirm Heuristic risk scores reflect accurately.
5. **Explainability**: View a node to observe GNN/Heuristic rationale text.
6. **Report**: Export a Markdown/CSV report and download.

## 5. Performance & Failure Recovery
- **Performance**:
  - Container Cold Start: < 20 seconds (Neo4j gating).
  - Graph Query Rendering: < 2 seconds.
- **Failures**:
  - Stop Neo4j (`docker compose stop neo4j`).
  - **Expectation**: Backend `health/ready` switches to 503. Frontend gracefully displays "Service Unavailable" boundaries.

## 6. Documentation Audit
- `deployment/docker.md` (Validated)
- `deployment/docker-compose.md` (Validated)
- `deployment/configuration.md` (Validated)
- `deployment/cicd.md` (Validated)
- `deployment/observability.md` (Validated)
- `deployment/security-hardening.md` (Validated)
