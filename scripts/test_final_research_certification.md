# Final Certification Testing Protocol

This document outlines the testing protocols established in Sprint 79.7 to programmatically enforce cross-document consistency and prevent human error in the final stages of the AgileGraph dissertation preparation.

## 1. Metric Consistency Regex Check
1. Execute the automated text-scraper utility: `grep -r "0.894" research/`.
2. **Verify**: Ensure this specific F1-score metric appears across `benchmark-study.md`, `statistical-analysis.md`, `ablation-study.md`, and `final-research-certification.md`.
3. Change the grep query to random numbers that *should not* exist (e.g., `0.95`). 
4. **Verify**: Ensure the query returns nothing, confirming no exaggerated metrics leaked into the documentation.

## 2. Evidence Traceability Test
1. Select a random claim from `final-research-certification.md` (e.g., "Heterogeneous Graph superiority is mathematically grounded in the ablation results").
2. **Verify Forward Link**: Open `research/ablation-study.md` and visually confirm the exact table rows supporting the `-0.053 F1 drop` exist.
3. **Verify Backward Link**: Ensure the underlying Python script generating that table row (`scripts/generate_ablation_figures.py`) has not been mutated or altered.

## 3. Empty Section Auditing
1. Scan all `.md` files in the `/research/` directory.
2. **Verify**: Ensure no `TODO`, `TBD`, or `[Insert Table Here]` placeholders remain in the documentation.
3. **Why**: Guarantees the dissertation draft will not inherit incomplete paragraphs or unresolved experimental blocks.

## 4. Reproducibility Execution Drill
1. Trigger the ultimate test: Run `docker system prune -a` (WARNING: Destructive) to clear the local image cache.
2. Execute `docker compose up --build`.
3. **Verify**: The entire stack must cold-compile successfully using purely the checked-in dependencies and Dockerfiles, without relying on stale, un-tracked local caching layers. This serves as the absolute final proof of replicability for future peer-reviewers.
