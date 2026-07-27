# Dashboard Frontend-Backend Alignment Testing

This document outlines the steps to verify that the FastAPI backend dashboard endpoints correctly align with the React frontend's TypeScript contracts.

## 1. Dashboard Summary
1. Navigate to `/api/v1/dashboard/summary` in the browser or via curl.
2. Verify the response is a JSON object that matches the `DashboardSummary` schema.
3. Validate that `kpis` contains keys: `totalAssets`, `critical`, `high`, `medium`, `low`, `migrationProgress`, `pqcReadiness`, `lastScan`.
4. Validate that `riskDistribution`, `algorithmUsage`, `departmentUsage`, `migrationTrend`, `recentScans`, `activity`, and `criticalAlerts` are arrays (empty arrays `[]` when data is unavailable, **never** `null` or missing).
5. Load the frontend Dashboard UI and confirm it renders without crashing (skeletons should disappear and empty state/0-values should render properly).

## 2. Dashboard Graph
1. Navigate to `/api/v1/dashboard/graph`.
2. Verify the response is a JSON object with `nodes` and `edges` arrays.
3. Verify each node has `id`, `label`, `type`, `risk`, `x`, `y`.
4. Verify each edge has `source` and `target`.
5. Load the frontend Graph page and confirm it handles the JSON payload gracefully.

## 3. Dashboard Reports
1. Navigate to `/api/v1/dashboard/reports`.
2. Verify the response is a JSON array `[]`.
3. If a report is generated, verify it matches the `ReportRecord` schema: `id`, `title`, `type`, `createdAt`, `size`, `author`.
4. Load the frontend Reports page and confirm it renders an empty list or the mock report object gracefully without crashing.

## 4. Dashboard Explanations
1. Navigate to `/api/v1/dashboard/explanations`.
2. Verify the response is a JSON array `[]` of Explanation objects.
3. Load the frontend Explainability page and confirm it handles the array successfully.

## 5. Type Validation
1. Verify `Dict[str, Any]` is removed from the return types of all endpoints in `app/api/routes/dashboard.py`.
2. Verify `Pydantic` models are enforced everywhere for the response models.
