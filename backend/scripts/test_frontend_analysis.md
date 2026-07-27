# Analysis Frontend-Backend Alignment Testing

This document outlines the steps to verify that the FastAPI backend analysis endpoints correctly align with the React frontend's TypeScript contracts for cryptographic assets.

## 1. Asset List (Risk Rankings)
1. Navigate to `/api/v1/analysis/assets?page=1&size=20` in the browser or via curl.
2. Verify the response is a JSON object matching `PaginatedAssetResponse`.
3. Validate that `items` is an array of objects matching the `AssetSummary` schema exactly (e.g. `id`, `name`, `type`, `riskScore`, etc. using camelCase aliases).
4. Load the frontend Risk Rankings page and confirm it renders the table rows correctly without missing data.
5. Change pagination parameters (`page=2`, `size=10`) and verify the `total`, `page`, and `size` fields reflect accurately.
6. Apply filtering and sorting parameters and verify the endpoint handles them gracefully.

## 2. Asset Detail (Single Asset)
1. Navigate to `/api/v1/analysis/assets/12345`.
2. Verify the response is a single JSON object matching the `AssetDetail` schema.
3. Validate the root properties match the `CryptoAsset` interface exactly.
4. Verify `heuristicBreakdown`, `connectedAssets`, `dependencies`, and `certificates` are returned as empty arrays `[]` if no data exists (Empty State Policy).
5. Verify `migrationProjection` and `explainability` objects return default numerical values `0` and empty strings `""` where appropriate.
6. Load the frontend Asset Details page and verify that clicking the different tabs (Overview, Technical, Dependencies, Connected, Risk, Migration) does not trigger secondary API calls or crash.

## 3. Empty Dataset & Missing Explainability
1. Force the Graph Query Service to return zero assets.
2. Verify `/assets` correctly returns `items: []` and `total: 0` without throwing a 500 error.
3. Verify `/assets/{asset_id}` still constructs an `AssetDetail` scaffold instead of missing the `explainability` and `migrationProjection` nodes.

## 4. Type Validation
1. Verify `Dict[str, Any]` is removed from the return types of all endpoints in `app/api/routes/analysis.py`.
2. Verify `Pydantic` models with `alias_generator=to_camel` are strictly enforced for the `AnalysisBaseModel`.
