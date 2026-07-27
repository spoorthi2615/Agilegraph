# Reports API Frontend-Backend Alignment Testing

This document outlines the steps to verify that the FastAPI backend report endpoints correctly serve the React Reports page without requiring the frontend to generate or process raw markdown files into UI elements.

## 1. Reports Listing Verification
1. Navigate to `/api/v1/reports` in your browser or REST client.
2. Verify the response is a paginated JSON object matching `PaginatedReportResponse`.
3. Validate that `items` contains an array of `ReportSummary` objects. (Should return `[]` strictly under the Empty State Policy when no reports exist).
4. Open the frontend Reports page and confirm the table/list renders properly without throwing `undefined` errors.

## 2. Report Detail & Preview Verification
1. Navigate to `/api/v1/reports/12345`.
2. Verify the response is a single JSON object matching `ReportDetail`.
3. Verify `metadata`, `statistics`, and `availableFormats` are fully populated.
4. Verify `preview` contains a `previewContent` string. This string should be lightweight (e.g., only the first 500 characters or the abstract) rather than transmitting a 5MB JSON string.
5. Open the frontend Report Details page and verify the UI seamlessly renders the abstract/preview and file statistics.

## 3. Streaming Download Verification
1. Use curl to trigger the download: `curl -i http://localhost:8000/api/v1/reports/12345/download?format=markdown`
2. Verify the `Content-Disposition` header dictates an attachment with `.md` extension.
3. Verify the `Transfer-Encoding` is `chunked` (or it streams properly) and doesn't load the whole file into RAM upfront.
4. Repeat for `?format=json` and `?format=csv` to ensure content types (`application/json`, `text/csv`) shift appropriately.
5. From the React frontend, click "Download" and ensure the browser natively saves the streamed file.

## 4. Empty Dataset Handlers
1. Ensure the system handles missing parameters and empty databases by explicitly returning `items: []` and empty metadata strings rather than `500 Internal Server Error` due to `NoneType` attribute access.
2. The frontend React component should show an "Empty State" component instead of a blank white screen.
