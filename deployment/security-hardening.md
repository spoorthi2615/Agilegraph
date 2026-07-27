# Deployment Security Hardening

This document outlines the defensive controls implemented in AgileGraph to secure the application against common OWASP vulnerabilities and deployment misconfigurations.

## 1. HTTP Security Headers
All backend responses are passed through a dedicated security middleware (`security_headers_middleware`) to enforce modern browser protections:
- `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing.
- `X-Frame-Options: DENY`: Prevents the application from being embedded in clickjacking iframes.
- `X-XSS-Protection: 1; mode=block`: Activates native browser cross-site scripting filters.
- `Referrer-Policy: strict-origin-when-cross-origin`: Strips URL paths when navigating to external domains to prevent accidental token leakage.
- `Content-Security-Policy`: Default strict policy (`default-src 'self'`).
- `Strict-Transport-Security` (HSTS): Enabled exclusively when `ENVIRONMENT=production` to force HTTPS.

## 2. CORS Hardening
The `allow_origins=["*"]` wildcard has been removed for production environments. 
If `ENVIRONMENT=production`, the application dynamically enforces a strict origin (e.g., `https://agilegraph.corp`) and rejects cross-origin spoofing. It explicitly limits `allow_methods` to required verbs instead of a wildcard.

## 3. Rate Limiting
A globally scoped rate limiter (`app.core.rate_limit`) protects heavy operations like GitHub Import, Analysis, and Report Generation from Denial of Service (DoS).
- Operational endpoints (`/health`, `/metrics`) bypass the limiter to ensure orchestration probes don't false-fail.
- Threshold: 60 requests per minute per IP address.

## 4. Container & Dependency Security
- Both backend and frontend Dockerfiles execute under non-root user contexts (`agilegraph` and `nginx`).
- Base images are pinned to minimal variants (`python:3.11-slim`, `node:20-alpine`, `nginx:alpine`) to reduce the available attack surface.
- The CI pipeline executes `pip-audit` and `npm audit --omit=dev` directly against the dependency trees to block deployments containing high/critical CVEs.

## 5. Secret Exposure
Zero embedded secrets exist in the repository. The application relies entirely on orchestrated environment variables via Docker Compose and fail-fast startup validation.
