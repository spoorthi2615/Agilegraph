# Security Hardening Validation Protocol

This document outlines the testing protocols established in Sprint 78.6 to verify the defensive security controls of AgileGraph.

## 1. HTTP Security Headers Test
1. Start the backend locally.
2. Run `curl -I http://localhost:8000/api/v1/health/live`.
3. **Verify**: The HTTP headers must include:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`
4. Set `.env` to `ENVIRONMENT=production`, restart, and verify `Strict-Transport-Security` is injected.

## 2. CORS Hardening Test
1. Set `ENVIRONMENT=production` in the `.env` file. Do NOT change `CORS_ORIGINS=*`.
2. Execute an `OPTIONS` preflight request mimicking a cross-origin browser:
   `curl -I -X OPTIONS -H "Origin: https://malicious.com" -H "Access-Control-Request-Method: GET" http://localhost:8000/api/v1/health/live`
3. **Verify**: The server must *not* reflect `Access-Control-Allow-Origin: *`. It should rigidly fallback to the internal strict origin or reject the preflight.

## 3. Rate Limiting Test
1. Rapidly execute the following loop in bash:
   `for i in {1..70}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/analysis/assets; done`
2. **Verify**: The first 60 requests should return `200` (or `4xx` depending on authentication/params). The subsequent requests must strictly return `429 Too Many Requests`.
3. Execute `curl -I http://localhost:8000/api/v1/metrics`.
4. **Verify**: The metrics endpoint returns `200` and ignores the rate limit penalty, proving orchestration probes will not be starved.

## 4. Container Permissions Test
1. Execute `docker run --rm -it agilegraph-backend:latest /bin/bash`.
2. Run `touch /usr/bin/malicious`.
3. **Verify**: The command must fail with `Permission denied`, proving the `agilegraph` user cannot mutate the system binaries or escalate privileges.
