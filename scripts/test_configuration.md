# Configuration & Secrets Testing Protocol

This document outlines the testing protocols established in Sprint 78.3 to ensure the configuration matrix and secret management systems are robust, secure, and fail-fast.

## 1. Fail-Fast Validation Test
1. Navigate to `/backend`.
2. Temporarily rename your local `.env` file to `.env.backup` to simulate a cold boot with no secrets.
3. Run `python -m app.main` or `uvicorn app.main:app`.
4. **Verify**: The application must immediately crash with a `pydantic.ValidationError` pointing to missing required fields (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`).
5. **Why**: This proves the backend will never boot into an undefined or default-secret state in a production environment.

## 2. Directory Validation Test
1. Restore your `.env` file.
2. Ensure the `uploads` and `reports` directories do NOT exist locally.
3. Run the backend normally.
4. **Verify**: Check the filesystem. The Pydantic validators (`@field_validator`) should have automatically created the missing directories during the configuration bootstrap phase.

## 3. Frontend Environment Injection Test
1. Navigate to `/frontend-1`.
2. Run a production build with a mock environment variable: `VITE_API_BASE_URL=https://mock.agilegraph.prod npm run build`.
3. Serve the `/dist` folder (e.g., via `npx serve -s dist`).
4. Open the Network tab in DevTools.
5. **Verify**: Ensure that API requests attempt to route to `https://mock.agilegraph.prod` rather than falling back to `localhost:8000`.

## 4. Environment Profiles Test
1. In the backend, set `ENVIRONMENT=production` in the `.env` file.
2. Start the application.
3. **Verify**: Inspect startup logs or `/health/live` to ensure the profile was registered correctly, confirming profile support works without code modifications.
