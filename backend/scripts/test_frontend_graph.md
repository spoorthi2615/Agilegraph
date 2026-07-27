# Graph API Frontend-Backend Alignment Testing

This document outlines the steps to verify that the FastAPI backend graph endpoints correctly serve the React Graph Canvas and Node details.

## 1. Graph Endpoint
1. Navigate to `/api/v1/graph`.
2. Verify the response is a JSON object matching `GraphResponse`.
3. Validate that `nodes` and `edges` arrays are successfully generated.
4. Verify `statistics` provides non-zero integers (e.g., `totalNodes`, `totalEdges`).
5. Verify `metadata` is populated with `repositoryName` and `graphSize`.
6. Apply filters (e.g., `?risk_level=critical`) and verify the `nodes` output is reduced appropriately.
7. Load the frontend Graph page and confirm it visualizes the nodes and edges correctly.

## 2. Node Detail Endpoint
1. Navigate to `/api/v1/graph/node/12345`.
2. Verify the response is a single JSON object matching `NodeDetails`.
3. Verify connections (`connectedAssets`, `incomingRelationships`, `outgoingRelationships`) are arrays.
4. Open the node side panel on the frontend UI and confirm all details render exactly.

## 3. Empty State Policy
1. Purge the database or mock a completely empty query.
2. Verify `/api/v1/graph` returns empty arrays `[]` instead of null or missing properties.
3. Validate statistics like `averageDegree` handle zero-division safely and return `0`.

## 4. Performance Requirements
1. Use an APM or the terminal logger to verify `get_high_risk_assets()` is invoked optimally without N+1 queries.
2. Ensure the node details fetch loads entirely from a single round trip to the server.
