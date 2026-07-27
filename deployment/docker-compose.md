# AgileGraph Docker Compose Deployment

This document outlines how to orchestrate the entire AgileGraph platform (Frontend, Backend, and Neo4j) using Docker Compose.

## Prerequisites
- Docker Engine 20.x or higher
- Docker Compose plugin (`docker compose`)

## Stack Overview
The Compose stack provisions three highly available, health-checked containers:
1. **Neo4j**: Graph database with persistent named volumes and a native cypher health check.
2. **Backend**: FastAPI Python layer running as a non-root user. Starts only after Neo4j is healthy.
3. **Frontend**: React SPA served via Nginx. Starts only after the Backend is healthy.

All services communicate over an isolated bridge network (`agilegraph-network`).

## 1. Quick Start

Ensure you are in the root directory (where `docker-compose.yml` resides) and run:
```bash
docker compose up -d
```
This will build the images (if not built already) and launch the stack in the background.

## 2. Environment Variables

Create a `.env` file in the same directory as the `docker-compose.yml` file to override default parameters:
```env
# Optional: Override the default Neo4j password
NEO4J_PASSWORD=my_secure_password
```

## 3. Stopping the Stack

To stop the containers safely without destroying persistent data:
```bash
docker compose stop
```

To stop and remove the containers, networks, and environment (persists named volumes):
```bash
docker compose down
```

To forcefully wipe the stack and ALL persistent named volumes (WARNING: destroys all graph data):
```bash
docker compose down -v
```

## 4. Rebuilding Images

If you have made code changes to the backend or frontend:
```bash
docker compose up -d --build
```

## 5. Viewing Logs

To stream the logs for the entire stack:
```bash
docker compose logs -f
```

To stream logs for a specific service (e.g., backend):
```bash
docker compose logs -f backend
```

## 6. Volumes & Persistence
The following named volumes are mapped to protect your data from container recreation:
- `agilegraph_neo4j_data`: Persists the physical graph store.
- `agilegraph_neo4j_logs`: Persists DB operational logs.
- `agilegraph_backend_uploads`: Persists ZIP and Git imports before processing.
- `agilegraph_backend_reports`: Persists generated markdown and CSV analysis reports.

## 7. Troubleshooting
- **Frontend can't reach Backend**: Ensure `VITE_API_BASE_URL` in the compose file's frontend build args matches the public URL of your backend. Because the React app runs in the user's browser, it cannot use internal Docker names like `http://backend:8000`.
- **Neo4j OOM**: The database memory is hardcapped in the compose file. If large graphs fail to load, increase `NEO4J_server_memory_heap_max__size` and the container's `memory` limit.
