# Configuration & Secrets Management

This document outlines the standardized configuration architecture for the AgileGraph platform, emphasizing secure secrets management, runtime validation, and environment profiling.

## Philosophy
1. **Centralized Settings**: All configurable values pass through Pydantic's `BaseSettings` on the backend, and Vite's `import.meta.env` on the frontend.
2. **Fail-Fast**: Missing required environment variables (e.g., database credentials) will crash the application immediately at boot to prevent undefined behavior in production.
3. **No Embedded Secrets**: Hardcoded passwords, API keys, or connection URIs have been strictly removed from the source code.

## Backend Configuration

Backend configuration is driven by `app.config.settings`. It natively parses `.env` files locally or container environment variables in production.

### Profiles
The `ENVIRONMENT` variable dictates application profile behavior:
- `development`: (Default) Assumes local bindings, debug logging.
- `testing`: Ephemeral database binds.
- `production`: Strictly enforces missing constraints, overrides CORS.

### Required Variables (No Defaults)
- `NEO4J_URI`: Connection string for Neo4j (e.g., `bolt://neo4j:7687`)
- `NEO4J_USERNAME`: Neo4j authentication user (e.g., `neo4j`)
- `NEO4J_PASSWORD`: Neo4j authentication password

### Optional Variables (With Safe Defaults)
- `HOST`: Bind address (default: `0.0.0.0`)
- `PORT`: Bind port (default: `8000`)
- `UPLOAD_DIRECTORY`: Location to save incoming ZIP/Git artifacts (default: `uploads`)
- `REPORT_DIRECTORY`: Location to save generated Markdown/CSV reports (default: `reports`)
- `LOG_LEVEL`: Application logging verbosity (default: `INFO`)
- `CORS_ORIGINS`: Allowed origins (default: `*`)

## Frontend Configuration

The React frontend leverages Vite's environment management. 

### Required Variables
- `VITE_API_BASE_URL`: The fully qualified public URL to the AgileGraph backend (e.g., `https://api.agilegraph.corp/api/v1`). If omitted, defaults to `http://localhost:8000/api/v1` for local development.

### Development `.env` Example
Create a file named `.env` in `/backend`:
```env
ENVIRONMENT=development
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=local_secret
UPLOAD_DIRECTORY=./local_uploads
```

### Production Deployment Notes
When deploying to orchestration platforms (Kubernetes, AWS ECS, Docker Swarm):
1. Never commit `.env` files.
2. Inject secrets directly via native Vault or Secrets Manager integrations.
3. Bind the `UPLOAD_DIRECTORY` and `REPORT_DIRECTORY` to persistent shared volumes (e.g., EFS or NFS) if running multiple backend replicas.
