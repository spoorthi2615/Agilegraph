# Dockerization Test Plan

This document outlines the testing protocols established in Sprint 78.1 to verify that the Docker images for AgileGraph are production-ready.

## 1. Build Verification
1. Navigate to `/backend`. Run `docker build -t agilegraph-backend:test .`. Verify the build completes successfully and utilizes the multi-stage layer cache.
2. Navigate to `/frontend-1`. Run `docker build -t agilegraph-frontend:test .`. Verify the build completes successfully and generates the static assets before switching to the Nginx alpine image.
3. Run `docker image ls` and verify the final image sizes are optimized (e.g. Frontend < 50MB, Backend Python slim < 300MB).

## 2. Container Startup Verification
1. Run the backend container using: `docker run --rm -p 8000:8000 agilegraph-backend:test`.
2. Inspect the terminal output and verify `Uvicorn running on http://0.0.0.0:8000` is present.
3. Run the frontend container using: `docker run --rm -p 8080:80 agilegraph-frontend:test`.
4. Navigate to `http://localhost:8080` in a browser and verify the React application loads successfully without 403 Forbidden Nginx errors.

## 3. Security & Context Verification
1. Open an interactive shell in the running backend container: `docker exec -it <container_id> /bin/bash`.
2. Run `whoami`. Verify the output is `agilegraph` and NOT `root`.
3. Open an interactive shell in the frontend container: `docker exec -it <container_id> /bin/sh`.
4. Run `whoami`. Verify the output is `nginx` and NOT `root`.

## 4. Environment Variables Validation
1. Start the backend container with a mock flag: `-e NEO4J_URI=bolt://mock:7687`.
2. Verify via `/api/v1/health` (or by inspecting the boot logs) that the application attempts to respect the overridden environment variable rather than hardcoded `.env` secrets.

## 5. Artifact Exclusion (.dockerignore)
1. Shell into the backend container and navigate to `/app`. Verify that `.git`, `.venv`, and local `__pycache__` directories do NOT exist inside the container.
2. Shell into the frontend container and navigate to `/usr/share/nginx/html`. Verify that `node_modules` and `.git` are not accidentally packaged into the web root.
