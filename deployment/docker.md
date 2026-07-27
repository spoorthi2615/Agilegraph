# AgileGraph Docker Deployment Guide

This guide details how to build and run the containerized backend and frontend services for AgileGraph.

## Prerequisites
- Docker Engine 20.x or higher
- Docker Compose (optional, for orchestrated deployment)

## 1. Backend Service

The AgileGraph backend is packaged as an optimized, multi-stage Python 3.11 slim image running as a non-root user.

### Build Instructions
Execute the following from the `/backend` directory:
```bash
docker build -t agilegraph-backend:latest .
```

### Run Instructions
```bash
docker run -d \
  --name agilegraph-backend \
  -p 8000:8000 \
  -e NEO4J_URI=bolt://neo4j:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=secret \
  agilegraph-backend:latest
```

### Environment Variables
- `NEO4J_URI`: Connection string for the Neo4j instance.
- `NEO4J_USER`: Neo4j authentication user.
- `NEO4J_PASSWORD`: Neo4j authentication password.
- `CORS_ORIGINS`: Comma-separated list of allowed origins.

---

## 2. Frontend Service

The AgileGraph frontend is built via a Node.js stage and served statically via an optimized Nginx alpine layer running as a non-root `nginx` user.

### Build Instructions
Execute the following from the `/frontend-1` directory. Be sure to inject the API URL at build time if overriding the default.
```bash
docker build --build-arg VITE_API_BASE_URL=http://api.agilegraph.local/api/v1 -t agilegraph-frontend:latest .
```

### Run Instructions
```bash
docker run -d \
  --name agilegraph-frontend \
  -p 80:80 \
  agilegraph-frontend:latest
```

### Troubleshooting
- **Frontend API Errors**: Since the frontend is a SPA served by Nginx, the `VITE_API_BASE_URL` must point to a domain resolvable by the *client's browser*, not the Docker internal network.
- **Backend File Permissions**: The backend runs as the `agilegraph` user. If mounting host volumes to `/app/uploads` or `/app/data`, ensure the host directory permissions allow UID 999 (default for useradd) to write to them.
