# Frontend API Testing Guide

This document outlines how to manually verify the robustness of the production API wrapper.

## 1. Environment Variables
1. Remove `.env` or set `VITE_API_BASE_URL=` to an empty string.
2. Verify the application falls back safely to `http://localhost:8000/api/v1` for network requests.
3. Set `VITE_API_BASE_URL=http://localhost:8000/api/v1` in your `.env` file and verify requests are routed correctly.

## 2. Timeout
1. Open `src/services/api-client.ts` and temporarily set `DEFAULT_TIMEOUT = 100` (100ms).
2. Load the dashboard.
3. Verify the request is aborted and throws an `ApiError` with `status: 408` and code `TIMEOUT_ERROR`.
4. The UI should display the error gracefully in the fallback boundary.
5. Revert the timeout back to 30000ms.

## 3. Invalid URL
1. Set `VITE_API_BASE_URL=http://invalid-url.local` in `.env`.
2. Load the application.
3. Verify the browser fails to resolve the DNS.
4. Verify the fetch wrapper catches the network failure and throws an `ApiError` with `status: 500` and code `NETWORK_ERROR`.

## 4. Backend Offline
1. Ensure the FastAPI backend is **stopped** (`Ctrl+C` the `uvicorn` process).
2. Load the application.
3. Verify the fetch wrapper catches the `ERR_CONNECTION_REFUSED` error.
4. Verify it correctly maps to an `ApiError` with `status: 500` and code `NETWORK_ERROR`.

## 5. 404 Not Found
1. In `src/services/api.ts`, temporarily change an endpoint string, e.g., `apiClient.get<DashboardSummary>("/invalid-endpoint")`.
2. Load the application.
3. Verify the backend responds with a 404 status.
4. Verify the fetch wrapper parses the 404 response, extracting the backend's JSON error detail.
5. Verify an `ApiError` is thrown with `status: 404` and the appropriate backend message.
6. Revert the endpoint string.

## 6. 500 Internal Server Error
1. In the backend, temporarily raise an `Exception("Test 500 error")` in an endpoint (e.g., `/api/v1/dashboard/summary`).
2. Load the application.
3. Verify the backend returns a 500 status.
4. Verify the fetch wrapper captures the 500 status code and message.
5. Verify an `ApiError` is thrown with `status: 500`.

## 7. Successful Request (200 OK)
1. Ensure the backend is running and endpoints are aligned.
2. Load the application.
3. Verify the dashboard successfully displays data without any ApiErrors.
4. Open the Network tab to ensure requests match the expected types and responses are correctly cast.
