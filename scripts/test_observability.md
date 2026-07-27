# Observability Testing Protocol

This document outlines the testing protocols established in Sprint 78.5 to verify the logging, correlation, and metrics components of the AgileGraph backend.

## 1. JSON Logging Format Test
1. Set the `.env` variable `LOG_LEVEL=INFO`.
2. Boot the backend server.
3. Observe the stdout console.
4. **Verify**: Every output line must be a valid JSON dictionary containing `timestamp`, `level`, `message`, `module`, and `process`. Raw string text or generic ASGI standard output logs should no longer be visible.

## 2. Correlation ID Pipeline Test
1. Execute a cURL command supplying a custom correlation ID:
   `curl -i -H "X-Request-ID: TRACE-9988" http://localhost:8000/api/v1/metrics`
2. **Verify Response**: The HTTP headers returned by the server must include `X-Request-ID: TRACE-9988`.
3. **Verify Logs**: The backend console must output the request completion log, and the JSON payload must include `"request_id": "TRACE-9988"`.
4. Execute a secondary command *without* the header.
5. **Verify**: The server must auto-generate a valid UUIDv4 for both the response header and internal logs.

## 3. Metrics Validation Test
1. Hit the `/api/v1/metrics` endpoint multiple times.
2. Check the JSON payload.
3. **Verify**: The `uptime_seconds` should continuously increase.
4. **Verify**: The `requests_total` counter should accurately reflect the traffic volume handled by the middleware.
5. Induce a 404 (e.g., fetch `/api/v1/does_not_exist`) and confirm that `errors_total` accurately increments.

## 4. Exception Sanitization Test
1. Force an unhandled exception (e.g., inject a `raise RuntimeError("Test Error")` inside a safe endpoint temporarily).
2. Execute the endpoint.
3. **Verify Client Side**: The client receives a sanitized `500 Internal Server Error` without stack traces.
4. **Verify Server Side**: The JSON log outputs `"level": "ERROR"`, successfully serializes the traceback under the `exception` key, and explicitly ties the failure to the `request_id`.
