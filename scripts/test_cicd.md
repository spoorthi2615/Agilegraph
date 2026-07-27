# CI Pipeline Validation Protocol

This document outlines the testing protocols established in Sprint 78.4 to verify the integrity and correct execution of the AgileGraph GitHub Actions CI pipeline.

## 1. Syntax Validation
1. Ensure `act` (a tool to run GitHub Actions locally) is installed on your machine.
2. Run `act push -n` (dry-run).
3. **Verify**: The YAML syntax parses successfully without complaining about invalid keys, missing steps, or incorrect matrix parameters.

## 2. Backend Pipeline Local Execution
1. Navigate to `/backend`.
2. Run `pip-audit --desc on` and verify it identifies high/critical CVEs if any exist.
3. Run `pytest` and confirm it generates a `coverage.xml`.
4. Run `black --check .` and `ruff check .` to verify formatting enforcement.

## 3. Frontend Pipeline Local Execution
1. Navigate to `/frontend-1`.
2. Run `npm ci` to verify the `package-lock.json` is perfectly synchronized with `package.json`.
3. Run `npm run build`.
4. **Verify**: The TypeScript compiler (`tsc`) exits with code `0`. If any type definitions are missing or misaligned, the build should fail.
5. Run `npm audit --omit=dev --audit-level=high` and verify exit logic based on vulnerability reports.

## 4. GitHub Actions Output Validation
1. Push a commit to an open Pull Request on the `main` branch.
2. Open the GitHub Actions tab.
3. **Verify**: The workflow is triggered automatically via the `pull_request` hook.
4. **Verify**: The `backend-ci` and `frontend-ci` jobs run in parallel, minimizing execution time.
5. **Verify**: The `docker-ci` job remains in a "Pending" state until both language-specific builds pass.
6. **Verify**: The `backend-coverage` XML file appears under the "Artifacts" section in the workflow summary page.
