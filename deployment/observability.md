# Observability & Monitoring

This document details the production observability stack configured for AgileGraph.

## 1. Centralized Logging Framework
The AgileGraph backend entirely discards Python's native `basicConfig` in favor of a centralized JSON-structured formatting layer (`app.core.logging`). 

### Key Features
- **JSON Format**: All output lines are valid JSON strings designed for automated consumption by systems like ELK (Elasticsearch/Logstash/Kibana) or Datadog.
- **Dynamic Levelling**: Controlled by the `LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **Context Injection**: Every single log emitted (even deep within domain services) natively includes the current `process` ID, `thread` ID, timestamp, module name, and execution `environment`.

## 2. Correlation IDs (`X-Request-ID`)
To trace user requests across asynchronous code execution:
- The logging middleware intercepts every HTTP request.
- If the caller provides an `X-Request-ID` header, it is retained. Otherwise, a fresh UUIDv4 is generated.
- The ID is stored in a `ContextVar` (`request_id_ctx`), meaning all logs emitted within that request's lifecycle will carry the ID, regardless of how deep the call stack goes.
- The backend always returns `X-Request-ID` in the HTTP response headers for frontend tracking.

## 3. Operational Middleware
The backend application utilizes custom middleware that:
- Logs standard request start/completion milestones.
- Intercepts **unhandled exceptions** before they crash the ASGI worker. It logs the stack trace internally but returns a sanitized 500 error to the client to avoid leaking proprietary source code or database schemas.

## 4. Metrics & Health Endpoint
AgileGraph distinguishes between business endpoints (`/api/v1/analysis`) and operational endpoints (`/api/v1/metrics`, `/health/ready`).

### `GET /api/v1/metrics`
Exposes high-level performance and stability aggregations in standard JSON:
```json
{
  "uptime_seconds": 12450,
  "requests_total": 850,
  "errors_total": 4,
  "successful_requests": 846,
  "application_version": "1.0.0",
  "environment": "production"
}
```
*Note: This acts as the pre-Prometheus baseline for immediate operational visibility.*
