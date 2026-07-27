# Explainability API Frontend-Backend Alignment Testing

This document outlines the steps to verify that the FastAPI backend explainability endpoints correctly serve the React Explainability visualization page without requiring the frontend to compute heuristic or GNN results.

## 1. Explainability Endpoint Verification
1. Navigate to `/api/v1/explainability/12345` in your browser or REST client.
2. Verify the response is a single JSON object matching `ExplainabilityResponse`.
3. Validate that the root payload contains `assetInformation`, `gnnExplanation`, `heuristicExplanation`, `migrationRecommendation`, `confidenceMetrics`, `naturalLanguageSummary`, and `metadata`.
4. Validate that the `naturalLanguageSummary` is pre-computed string text.
5. Verify no objects inside `gnnExplanation` or `heuristicExplanation` return `null`. (They should return empty lists `[]` or `0` due to the strict Empty State Policy enforced in Pydantic models).

## 2. Feature & Edge Importance 
1. Drill down into `gnnExplanation`.
2. Validate that `featureImportance` and `importantEdges` are present as arrays of objects.
3. Open the frontend Explainability page and confirm the GNN visualizer renders the nodes/edges and lists the feature weights exactly as transmitted by the backend.

## 3. Heuristic & Migration Data
1. Drill down into `heuristicExplanation.breakdown`.
2. Validate that the `riskFormulaBreakdown` and `penaltyBreakdown` strings are present.
3. Open the frontend and confirm the Heuristic Breakdown cards render correctly without throwing undefined errors.
4. Verify the frontend renders the Migration Recommendation (e.g. `ML-KEM-768`) and priority straight from `migrationRecommendation`.

## 4. Frontend Independence Test
1. Disconnect the Neo4j backend or mock an empty query resolution internally in the backend router.
2. Verify the FastAPI layer intercepts the failure and emits an empty-state `ExplainabilityResponse` (metrics set to `0` or `""`).
3. Load the frontend page. Verify it renders skeletons or safe '0' default widgets, confirming the UI contains zero unhandled interpretation logic for edge-cases.
