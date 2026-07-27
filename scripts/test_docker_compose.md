# Docker Compose Validation Protocol

This document outlines the testing protocols established in Sprint 78.2 to verify that the AgileGraph Docker Compose orchestration boots reliably, maintains internal networking, and persists data correctly.

## 1. Startup Ordering & Health Checks
1. Ensure the daemon is clear. Run `docker compose down -v`.
2. Run `docker compose up -d`.
3. Immediately run `docker ps` or `docker compose ps`.
4. Observe the `STATUS` column. Verify that `agilegraph-neo4j` enters `(health: starting)`, while `agilegraph-backend` waits.
5. Verify that once `agilegraph-neo4j` transitions to `(healthy)`, `agilegraph-backend` begins starting.
6. Verify `agilegraph-frontend` waits for `agilegraph-backend` to reach `(healthy)`.

## 2. Inter-Service Networking
1. Open an interactive shell in the backend container: `docker exec -it agilegraph-backend /bin/bash`.
2. Attempt to ping Neo4j using the internal service name: `ping neo4j` (or use python to test connection to `bolt://neo4j:7687`).
3. Verify the resolution targets the internal bridge network IP rather than localhost.

## 3. Persistent Volume Behavior
1. Ensure the stack is running.
2. Hit the upload endpoint on the backend (via UI or cURL) to trigger an artifact generation inside `/app/uploads`.
3. Stop and destroy the container instances: `docker compose down`.
4. Re-launch the stack: `docker compose up -d`.
5. Shell into the backend: `docker exec -it agilegraph-backend /bin/bash` and navigate to `/app/uploads`.
6. Verify the uploaded artifact is still physically present on the volume.

## 4. Resource & Restart Policies
1. Run `docker stats`. Verify that `agilegraph-neo4j` respects the 2GB memory boundary and does not monopolize host RAM.
2. Force kill the backend container: `docker kill agilegraph-backend`.
3. Run `docker compose ps` repeatedly. Verify that Docker detects the unexpected exit and automatically restarts the container due to the `unless-stopped` policy.
